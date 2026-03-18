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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

RATE_WINDOW = 30
RATE_MAX = 20
_hits = {}

def rate_limit(ip: str):
    now = time.time()
    arr = _hits.get(ip, [])
    arr = [t for t in arr if now - t < RATE_WINDOW]
    if len(arr) >= RATE_MAX:
        raise HTTPException(status_code=429, detail="Too many requests.")
    arr.append(now)
    _hits[ip] = arr


CUE_SYSTEM = """Tu es l'assistant support officiel de CUE, une plateforme de booking DJ.

INFOS CUE :
- CUE connecte DJs vérifiés avec clubs, venues, mariages, événements privés
- Fonctions : matching IA, contrats automatiques, paiement Stripe, avis vérifiés

TARIFS :
- Starter : GRATUIT, 7% commission
- Pro DJ : 29€/mois, 3% commission, contrats IA illimités, badge Pro, priorité matching, analytics
- Business : 149€/mois, 0% commission, multi-users, API, account manager

COMPTE :
- Inscription : cliquer S'inscrire, email + mdp, valider par email
- Mot de passe oublié : bouton dédié sur la page connexion
- Vérification identité obligatoire

BOOKING :
- Processus : Demande → Acceptation → Paiement → Confirmation → Event → Validation → Avis
- Annulation : possible selon conditions définies à la confirmation (frais possibles)
- Modification booking confirmé : accord des deux parties requis
- No-show : signaler depuis le booking immédiatement
- Communication : uniquement via chat intégré CUE

PAIEMENTS :
- Via Stripe, sécurisé
- Acompte 50% + solde 50% après événement
- DJ payé après validation
- Factures dans onglet Transactions

TRANSPORT & MATOS :
- Transport non inclus, à négocier entre DJ et venue, ajout possible dans clauses contrat
- Matériel son : dépend du venue, vérifier fiche technique avant confirmation

PROFIL DJ :
- Ajouter bio, genres, références, extraits audio, dispos
- Calendrier dans tableau de bord

PROFIL VENUE :
- Localisation, capacité, styles, fiche technique (audio, DJ booth, éclairage)
- Créer événement : date, budget, styles, conditions

CONTRATS :
- Générés par IA en 30 secondes, 10 sections légales

CONTACT : cue.dj.app@gmail.com | +33 7 67 01 15 32

RÈGLES :
- Réponds dans la langue de l'utilisateur
- Sois chaleureux et concis (max 3 phrases)
- Comprends les fautes de frappe (ceu=CUE, abo=abonnement, matos=matériel, inscire=inscrire)
- Ne pas inventer d'infos non listées"""


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
    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=CUE_SYSTEM,
            messages=[{"role": "user", "content": msg}]
        )
        return ChatOut(reply=message.content[0].text, sources=[], escalation=False)
    except Exception:
        return ChatOut(
            reply="Problème technique. Contactez-nous : cue.dj.app@gmail.com",
            sources=[], escalation=True
        )


@app.post("/match")
async def match(payload: MatchIn, request: Request):
    ip = request.client.host if request.client else "unknown"
    rate_limit(ip)
    prompt = f"""Recommande 3 profils DJ fictifs pour cet événement.
Type: {payload.type} | Vibe: {payload.vibe} | Budget: {payload.budget} | Ville: {payload.city} | Détails: {payload.details}
Retourne UNIQUEMENT ce JSON (pas de markdown):
[{{"name":"DJ Nom","match":95,"tags":["House","Techno"],"price":"400€","bio":"2 phrases."}},{{"name":"DJ Nom2","match":88,"tags":["Tag1"],"price":"300€","bio":"2 phrases."}},{{"name":"DJ Nom3","match":82,"tags":["Tag1"],"price":"250€","bio":"2 phrases."}}]"""
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system="Expert booking DJ. JSON valide uniquement.",
            messages=[{"role": "user", "content": prompt}]
        )
        text = message.content[0].text.strip().replace("```json","").replace("```","").strip()
        return {"djs": json.loads(text)}
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
    prompt = f"""Génère un contrat DJ professionnel en français avec ces sections:
###SECTION_1: PARTIES### ###SECTION_2: OBJET### ###SECTION_3: DATE ET HORAIRES### ###SECTION_4: CONDITIONS FINANCIÈRES### ###SECTION_5: PAIEMENT### ###SECTION_6: ANNULATION### ###SECTION_7: RIDER TECHNIQUE### ###SECTION_8: DROITS D'IMAGE### ###SECTION_9: CLAUSE CUE### ###SECTION_10: SIGNATURES###
DJ: {payload.dj} | Venue: {payload.venue} | Date: {payload.date or 'À confirmer'} | Horaires: {payload.start}→{payload.end}
Cachet: {payload.fee}€ | Acompte: {deposit}€ | Solde: {balance}€ | Rider: {payload.rider or 'Standard'} | Clauses: {payload.clauses or 'Aucune'}"""
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            system="Expert juridique contrats prestation artistique française.",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"contract_text": message.content[0].text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
