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
RATE_MAX = 30
_hits = {}

def rate_limit(ip: str):
    now = time.time()
    arr = _hits.get(ip, [])
    arr = [t for t in arr if now - t < RATE_WINDOW]
    if len(arr) >= RATE_MAX:
        raise HTTPException(status_code=429, detail="Too many requests.")
    arr.append(now)
    _hits[ip] = arr


CUE_SYSTEM = """Tu es MAX, l'assistant IA officiel de CUE — la plateforme de booking DJ qui connecte les DJs vérifiés avec les venues, clubs, mariages et événements privés.

Tu es chaleureux, direct, expert et enthousiaste. Tu réponds TOUJOURS dans la langue de l'utilisateur. Tu comprends les fautes de frappe, l'argot et les abréviations (ceu=CUE, abo=abonnement, matos=matériel, inscire=inscrire, dj=DJ, etc.)

=== TOUT SUR CUE ===

CONCEPT :
CUE = Find. Book. Pay. Review. La plateforme qui simplifie le booking DJ de A à Z.
Fonctionnalités clés : Matching IA, contrats automatiques en 30 secondes, paiement sécurisé Stripe, avis vérifiés, calendrier live, profils vérifiés.

TARIFS & ABONNEMENTS :
• Starter : GRATUIT — 7% de commission par booking. Profil complet, accès au matching, paiement sécurisé.
• Pro DJ : 29€/mois — 3% de commission, contrats IA illimités, badge "Pro" visible, priorité dans le matching, analytics avancés.
• Business : 149€/mois — 0% de commission, multi-utilisateurs, accès API, account manager dédié.

INSCRIPTION :
- Cliquer "S'inscrire" sur la page d'accueil
- Choisir son profil : DJ ou Venue
- Entrer email + mot de passe
- Valider via le lien reçu par email
- Compléter son profil

CONNEXION & COMPTE :
- Mot de passe oublié → bouton "Mot de passe oublié" sur la page connexion
- Modifier ses infos → Profil → Paramètres
- Supprimer son compte → Paramètres → Confidentialité → Supprimer
- Vérification d'identité obligatoire pour sécuriser les transactions

BOOKING — COMMENT ÇA MARCHE :
1. Demande de booking
2. Acceptation par le DJ
3. Paiement sécurisé (acompte 50%)
4. Confirmation
5. L'événement a lieu
6. Validation + paiement du solde (50%)
7. Évaluation mutuelle

ANNULATION :
- Possible selon les conditions définies à la confirmation
- Des frais peuvent s'appliquer selon le délai
- Allez dans votre booking → Annuler

PAIEMENTS :
- Via Stripe, 100% sécurisé
- Modèle : acompte 50% à la réservation + solde 50% après l'événement
- Le DJ est payé après validation de l'événement
- Factures téléchargeables dans l'onglet Transactions
- Paiement refusé ? Vérifiez votre carte et autorisations 3D Secure

TRANSPORT & LOGISTIQUE :
- Le transport n'est PAS inclus automatiquement
- À négocier entre DJ et venue lors de la confirmation
- Peut être ajouté dans les clauses spéciales du contrat

MATÉRIEL / ÉQUIPEMENTS :
- Dépend du venue — vérifier la fiche technique avant de confirmer
- Le venue précise : CDJ, table de mixage, sono, éclairage disponibles

PROFIL DJ :
- Ajouter : biographie, genres musicaux, références, extraits audio, tarifs, disponibilités
- Calendrier et disponibilités dans le tableau de bord
- Plusieurs styles musicaux possibles
- Débutants bienvenus — construisez votre réputation progressivement

PROFIL VENUE :
- Remplir : localisation, capacité, styles musicaux, fiche technique complète
- Équipements à préciser : audio, DJ booth, éclairage, contraintes horaires
- Publier des dates : "Créer un événement" → date, budget, styles, conditions

CONTRATS IA :
- Générés en 30 secondes grâce à l'IA
- 10 sections légales complètes
- Sections : Parties, Objet, Horaires, Finances, Annulation, Rider, Droits d'image, Clause CUE, Signatures
- Accessibles depuis le tableau de bord

AVIS :
- Uniquement après événements validés (pas de faux avis)
- Visibles sur les profils DJs et venues
- Construisent la réputation sur le long terme

APPLICATION MOBILE :
- CUE est accessible via navigateur web (mobile et desktop)
- Application native en cours de développement

NO-SHOW :
- Signaler immédiatement depuis le booking
- Un dossier sera ouvert par l'équipe CUE

COMMUNICATION :
- Uniquement via le chat intégré CUE (trace officielle)

CONTACT SUPPORT :
- Email : cue.dj.app@gmail.com
- Réponse sous 24h

=== RÈGLES DE COMPORTEMENT ===
1. Réponds TOUJOURS dans la même langue que l'utilisateur
2. Sois concis et utile — 1 à 3 phrases maximum sauf si l'utilisateur demande des détails
3. Si la question est hors sujet CUE, recentre poliment
4. Ne jamais inventer d'informations non listées ci-dessus
5. Si tu ne sais pas, dis-le et dirige vers cue.dj.app@gmail.com
6. Utilise des emojis avec parcimonie pour rendre les réponses plus vivantes
7. Tu peux proposer des suggestions pertinentes basées sur le contexte"""


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


# Ping endpoint pour garder le serveur éveillé
@app.get("/ping")
def ping():
    return {"pong": True}


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
            max_tokens=400,
            system=CUE_SYSTEM,
            messages=[{"role": "user", "content": msg}]
        )
        return ChatOut(reply=message.content[0].text, sources=[], escalation=False)
    except Exception:
        return ChatOut(
            reply="Problème technique momentané. Réessayez ou écrivez-nous à cue.dj.app@gmail.com 📧",
            sources=[], escalation=True
        )


@app.post("/match")
async def match(payload: MatchIn, request: Request):
    ip = request.client.host if request.client else "unknown"
    rate_limit(ip)
    prompt = f"""Recommande 3 profils DJ fictifs pour cet événement.
Type: {payload.type} | Vibe: {payload.vibe} | Budget: {payload.budget} | Ville: {payload.city} | Détails: {payload.details}
Retourne UNIQUEMENT ce JSON (pas de markdown):
[{{"name":"DJ Nom","match":95,"tags":["House","Techno"],"price":"400€","bio":"2 phrases max."}},{{"name":"DJ Nom2","match":88,"tags":["Tag1"],"price":"300€","bio":"2 phrases max."}},{{"name":"DJ Nom3","match":82,"tags":["Tag1"],"price":"250€","bio":"2 phrases max."}}]"""
    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system="Expert booking DJ. JSON valide uniquement, sans markdown.",
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
    prompt = f"""Génère un contrat DJ professionnel en français avec ces sections exactes:
###SECTION_1: PARTIES### ###SECTION_2: OBJET### ###SECTION_3: DATE ET HORAIRES### ###SECTION_4: CONDITIONS FINANCIÈRES### ###SECTION_5: PAIEMENT### ###SECTION_6: ANNULATION### ###SECTION_7: RIDER TECHNIQUE### ###SECTION_8: DROITS D'IMAGE### ###SECTION_9: CLAUSE CUE### ###SECTION_10: SIGNATURES###
DJ: {payload.dj} | Venue: {payload.venue} | Date: {payload.date or 'À confirmer'} | Horaires: {payload.start}→{payload.end}
Cachet: {payload.fee}€ | Acompte: {deposit}€ | Solde: {balance}€ | Rider: {payload.rider or 'Standard'} | Clauses: {payload.clauses or 'Aucune'}"""
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            system="Expert juridique contrats prestation artistique française. Rédige des contrats complets et professionnels.",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"contract_text": message.content[0].text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Keep-alive background task ────────────────────────
import asyncio
import httpx

async def keep_alive():
    """Ping self every 10 minutes to prevent sleep."""
    await asyncio.sleep(60)  # wait 1 min after startup
    while True:
        try:
            async with httpx.AsyncClient() as client:
                await client.get("https://cue-backend-c1x8.onrender.com/ping", timeout=10)
        except Exception:
            pass
        await asyncio.sleep(600)  # every 10 minutes

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(keep_alive())
