from fastapi.middleware.cors import CORSMiddleware
import os
import time
import json
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

load_dotenv()

app = FastAPI(title="CUE Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod: limiter à votre domaine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Client Anthropic ──────────────────────────────────────
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ── Rate limiting ─────────────────────────────────────────
RATE_WINDOW = 30
RATE_MAX = 20
_hits = {}

def rate_limit(ip: str):
    now = time.time()
    arr = _hits.get(ip, [])
    arr = [t for t in arr if now - t < RATE_WINDOW]
    if len(arr) >= RATE_MAX:
        raise HTTPException(status_code=429, detail="Too many requests. Please retry shortly.")
    arr.append(now)
    _hits[ip] = arr


# ── FAQ ───────────────────────────────────────────────────
FAQ_PATH = "faq_seed.json"

def load_faq():
    """
    Accepte 2 formats :
    A) {"items":[{"id":"...","q":"...","a":"..."}]}
    B) [{"category":"...","question":"...","variants":[...],"short_answer":"...","long_answer":"..."}]
    """
    try:
        with open(FAQ_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and isinstance(data.get("items"), list):
            items = data["items"]
            normalized = []
            for i, it in enumerate(items):
                normalized.append({
                    "id": it.get("id") or f"FAQ-{i+1:03d}",
                    "q": it.get("q") or "",
                    "a": it.get("a") or "",
                    "category": it.get("category"),
                    "tags": it.get("tags", []),
                    "variants": it.get("variants", []),
                })
            return normalized

        if isinstance(data, list):
            normalized = []
            for i, it in enumerate(data):
                q = it.get("question") or ""
                a = it.get("long_answer") or it.get("short_answer") or ""
                normalized.append({
                    "id": f"QNA-{i+1:03d}",
                    "q": q,
                    "a": a,
                    "category": it.get("category"),
                    "tags": [],
                    "variants": it.get("variants", []),
                })
            return normalized

        return []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        raise RuntimeError(f"faq_seed.json invalide (JSON cassé): {e}")


FAQ_ITEMS = load_faq()

def search_faq(question: str, items, top_k: int = 3):
    q_words = set(w.strip(".,!?;:()[]").lower() for w in question.split() if len(w) > 2)
    scored = []
    for item in items:
        q = (item.get("q") or "").lower()
        a = (item.get("a") or "").lower()
        variants = " ".join(item.get("variants") or []).lower()
        text = q + " " + variants + " " + a
        score = sum(1 for w in q_words if w in text)
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


# ── Modèles ───────────────────────────────────────────────
class ChatIn(BaseModel):
    message: str

class ChatOut(BaseModel):
    reply: str
    sources: list[str] = []
    escalation: bool = False

class MatchIn(BaseModel):
    type: str
    vibe: str = "Non précisé"
    budget: str
    city: str = "Non précisée"
    details: str = "Aucun"

class ContractIn(BaseModel):
    dj: str
    venue: str
    date: str = ""
    start: str = "23:00"
    end: str = "05:00"
    fee: float = 0
    rider: str = ""
    clauses: str = ""


# ── Routes ────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"ok": True}


@app.post("/chat", response_model=ChatOut)
async def chat(payload: ChatIn, request: Request):
    ip = request.client.host if request.client else "unknown"
    rate_limit(ip)

    msg = payload.message.strip()
    if not msg:
        raise HTTPException(status_code=400, detail="Empty message.")

    matches = search_faq(msg, FAQ_ITEMS)

    if matches:
        reply_text = "\n\n---\n\n".join(
            [f"Q: {m['q']}\nA: {m['a']}" for m in matches]
        )
        return ChatOut(
            reply=reply_text,
            sources=[m["id"] for m in matches],
            escalation=False
        )

    return ChatOut(
        reply=(
            "Je n'ai pas trouvé de réponse exacte.\n"
            "Tu peux préciser :\n"
            "1) Tu es DJ ou lieu ?\n"
            "2) C'est sur paiements, booking, compte, ou autre ?\n"
            "3) Si booking : date + ville ?\n"
        ),
        sources=[],
        escalation=True
    )


@app.post("/match")
async def match(payload: MatchIn, request: Request):
    ip = request.client.host if request.client else "unknown"
    rate_limit(ip)

    prompt = f"""Tu es un expert en booking DJ. Recommande 3 profils DJ fictifs et détaillés pour cet événement.
Type : {payload.type}
Vibe : {payload.vibe}
Budget : {payload.budget}
Ville : {payload.city}
Détails : {payload.details}

Retourne EXACTEMENT ce format JSON (rien d'autre, pas de markdown) :
[{{"name":"DJ Nom","match":95,"tags":["House","Techno"],"price":"400€","bio":"Description courte 2 phrases."}},{{"name":"DJ Nom2","match":88,"tags":["Tag1","Tag2"],"price":"300€","bio":"Description."}},{{"name":"DJ Nom3","match":82,"tags":["Tag1"],"price":"250€","bio":"Description."}}]"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system="Tu es expert en booking DJ et matching musical. Réponds uniquement en JSON valide, sans markdown.",
            messages=[{"role": "user", "content": prompt}]
        )
        text = message.content[0].text.strip()
        clean = text.replace("```json", "").replace("```", "").strip()
        djs = json.loads(clean)
        return {"djs": djs}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Erreur de parsing JSON depuis le modèle.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/contract")
async def contract(payload: ContractIn, request: Request):
    ip = request.client.host if request.client else "unknown"
    rate_limit(ip)

    if not payload.dj or not payload.venue:
        raise HTTPException(status_code=400, detail="Nom DJ et Venue requis.")

    deposit = round(payload.fee * 0.5 * 100) / 100
    balance = round((payload.fee - deposit) * 100) / 100

    prompt = f"""Génère un contrat de prestation DJ professionnel complet en français.
Utilise exactement ce format pour chaque section: ###SECTION_N: TITRE###

###SECTION_1: PARTIES###
###SECTION_2: OBJET DE LA PRESTATION###
###SECTION_3: DATE, LIEU ET HORAIRES###
###SECTION_4: CONDITIONS FINANCIÈRES###
###SECTION_5: MODALITÉS DE PAIEMENT###
###SECTION_6: POLITIQUE D'ANNULATION###
###SECTION_7: RIDER TECHNIQUE###
###SECTION_8: DROITS D'IMAGE ET D'ENREGISTREMENT###
###SECTION_9: CLAUSE PLATEFORME CUE###
###SECTION_10: SIGNATURES###

Informations :
DJ : {payload.dj} | Venue : {payload.venue}
Date : {payload.date or 'À confirmer'} | Horaires : {payload.start} → {payload.end}
Cachet total : {payload.fee}€ | Acompte 50% : {deposit}€ | Solde 50% : {balance}€
Rider : {payload.rider or 'Standard club'}
Clauses spéciales : {payload.clauses or 'Aucune'}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            system="Tu es expert juridique en contrats de prestation artistique française. Génère des contrats professionnels complets avec articles numérotés.",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"contract_text": message.content[0].text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
