from fastapi.middleware.cors import CORSMiddleware
import os
import time
import json
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CUE Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod: limiter
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


FAQ_PATH = "faq_seed.json"

def load_faq():
    """
    Accepte 2 formats:
    A) {"items":[{"id":"...","q":"...","a":"..."}]}
    B) [{"category":"...","question":"...","variants":[...],"short_answer":"...","long_answer":"..."}]
    """
    try:
        with open(FAQ_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Format A
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

        # Format B
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
    # on compare avec question + variants
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


class ChatIn(BaseModel):
    message: str

class ChatOut(BaseModel):
    reply: str
    sources: list[str] = []
    escalation: bool = False


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
            "Je n’ai pas trouvé de réponse exacte.\n"
            "Tu peux préciser :\n"
            "1) Tu es DJ ou lieu ?\n"
            "2) C’est sur paiements, booking, compte, ou autre ?\n"
            "3) Si booking : date + ville ?\n"
        ),
        sources=[],
        escalation=True
    )