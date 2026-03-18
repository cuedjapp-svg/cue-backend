from fastapi.middleware.cors import CORSMiddleware
import os
import time
import json
import re
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
        raise HTTPException(status_code=429, detail="Too many requests. Please retry shortly.")
    arr.append(now)
    _hits[ip] = arr

FAQ_ITEMS = [
    {"id":"F01","q":"Je ne parviens pas à me connecter","a":"Vérifiez votre email et mot de passe. Utilisez « Mot de passe oublié » si nécessaire.","variants":["connexion impossible","impossible de me connecter","login ne fonctionne pas","mot de passe oublié","je peux pas me connecter","ca marche pas connexion","probleme connexion","konexion","conection","connecter"]},
    {"id":"F02","q":"Je n'ai pas reçu l'email de validation","a":"Vérifiez vos courriers indésirables (spam). Vous pouvez renvoyer l'email depuis la page de connexion.","variants":["email non reçu","pas de mail","confirmation email","validation compte","email recu","mail reçu","pas reçu","mail pas arrivé"]},
    {"id":"F03","q":"Comment réinitialiser mon mot de passe ?","a":"Cliquez sur « Mot de passe oublié » sur la page de connexion, entrez votre email et suivez les instructions reçues.","variants":["reset password","changer mot de passe","nouveau mot de passe","oublié mot de passe","mdp oublié","password"]},
    {"id":"F04","q":"Comment modifier mes informations personnelles ?","a":"Allez dans Profil → Paramètres → Modifier les informations.","variants":["changer mes infos","modifier profil","mettre à jour informations","changer info","modifier info"]},
    {"id":"F05","q":"Comment supprimer mon compte ?","a":"Allez dans Paramètres → Confidentialité → Supprimer mon compte.","variants":["effacer compte","clôturer compte","désactiver compte","delete account","supprimer"]},
    {"id":"F06","q":"Pourquoi vérifier mon identité ?","a":"La vérification sécurise les transactions et assure la fiabilité des utilisateurs sur la plateforme.","variants":["vérification identité","KYC","pourquoi justificatif","verif identité","justificatif"]},
    {"id":"F07","q":"Combien de temps prend la vérification ?","a":"Quelques minutes en général. Un contrôle manuel peut parfois prolonger le délai.","variants":["délai vérification","temps validation","vérification lente","combien de temps verif"]},
    {"id":"F08","q":"Ma vérification est refusée","a":"Vérifiez la qualité et la validité de vos documents, puis soumettez à nouveau. Contactez le support si le problème persiste.","variants":["vérification rejetée","documents refusés","vérification échouée","refusé","rejeté"]},
    {"id":"F09","q":"Mes données sont-elles sécurisées ?","a":"Oui. CUE chiffre toutes les données sensibles et applique des standards de sécurité élevés.","variants":["sécurité données","confidentialité","RGPD","données personnelles","securite","mes données"]},
    {"id":"F10","q":"Comment signaler un comportement suspect ?","a":"Utilisez le bouton « Signaler » sur le profil ou dans le booking concerné.","variants":["signaler utilisateur","signaler problème","comportement inapproprié","signalement","reporter"]},
    {"id":"F11","q":"Comment optimiser mon profil DJ ?","a":"Ajoutez une biographie claire, vos genres musicaux, des références, des extraits audio et vos disponibilités.","variants":["améliorer profil","compléter profil DJ","meilleur profil","profil dj","mon profil dj"]},
    {"id":"F12","q":"Puis-je sélectionner plusieurs styles musicaux ?","a":"Oui, vous pouvez en sélectionner plusieurs. Assurez-vous qu'ils correspondent à votre univers artistique.","variants":["genres musicaux","styles de musique","plusieurs genres","style musique","genre musical"]},
    {"id":"F13","q":"Comment augmenter mes chances d'être sélectionné ?","a":"Maintenez un profil complet, accumulez des avis positifs et respectez toujours vos engagements.","variants":["plus de bookings","être choisi","visibilité DJ","plus de gigs","plus de boulot"]},
    {"id":"F14","q":"Mon profil est en attente de validation","a":"Une vérification qualité est en cours. Cela prend généralement quelques minutes.","variants":["profil en attente","validation profil","profil pas encore actif","attente validation"]},
    {"id":"F15","q":"Comment gérer mes disponibilités ?","a":"Dans votre tableau de bord, allez dans la section Calendrier et mettez à jour vos dates disponibles.","variants":["calendrier DJ","disponibilités","dates libres","agenda","dispo","disponible"]},
    {"id":"F16","q":"Comment créer un profil venue ?","a":"Sélectionnez « Venue » à l'inscription, puis complétez : localisation, capacité, styles musicaux et fiche technique.","variants":["inscription venue","créer compte lieu","profil club","profil salle","venue","salle"]},
    {"id":"F17","q":"Comment préciser les équipements disponibles ?","a":"Dans votre fiche technique, renseignez : système audio, DJ booth, éclairage et contraintes horaires.","variants":["matériel DJ","équipements salle","rider technique","CDJ","table de mixage","matos","equipement","materiel"]},
    {"id":"F18","q":"Comment publier une date à pourvoir ?","a":"Cliquez sur « Créer un événement », renseignez la date, le budget, les styles souhaités et les conditions.","variants":["publier soirée","créer événement","chercher DJ pour soirée","mettre une date","publier date","event"]},
    {"id":"F19","q":"Comment sélectionner un DJ ?","a":"Consultez les profils, écoutez les extraits audio, vérifiez les avis, puis confirmez le booking via la plateforme.","variants":["choisir DJ","trouver DJ","réserver DJ","chercher DJ","trouver un dj","book dj"]},
    {"id":"F20","q":"Puis-je modifier un événement publié ?","a":"Oui, tant que l'événement n'est pas encore confirmé par un DJ.","variants":["modifier soirée","changer événement","éditer date","modifier event","changer event"]},
    {"id":"F21","q":"Comment fonctionne un booking sur CUE ?","a":"Le processus : Demande → Acceptation → Paiement sécurisé → Confirmation → Événement → Validation → Évaluation.","variants":["processus booking","comment réserver","étapes réservation","comment ça marche","fonctionnement","ca marche comment","comment ca fonctionne"]},
    {"id":"F22","q":"Puis-je modifier un booking confirmé ?","a":"Oui, mais toute modification doit être validée par les deux parties.","variants":["changer booking","modifier réservation","annuler modification","modifier booking"]},
    {"id":"F23","q":"Que faire en cas de no-show ?","a":"Signalez immédiatement la situation depuis le booking pour qu'un dossier soit ouvert.","variants":["DJ absent","no show","DJ pas venu","artiste absent","pas venu","annulé au dernier moment"]},
    {"id":"F24","q":"Comment contacter l'autre partie ?","a":"Utilisez uniquement le chat intégré CUE pour conserver une trace officielle de vos échanges.","variants":["contacter DJ","messagerie","chat plateforme","envoyer message","message","contacter venue","comment écrire"]},
    {"id":"F25","q":"Comment annuler un booking ou un événement ?","a":"Oui, vous pouvez annuler selon les conditions définies à la confirmation. Allez dans votre booking → Annuler. Des frais peuvent s'appliquer selon le délai d'annulation.","variants":["annuler réservation","annulation booking","annuler event","annuler soirée","comment annuler","annulation","cancel","annulé","supprimer booking","je veux annuler"]},
    {"id":"F26","q":"Comment les paiements sont-ils sécurisés ?","a":"Les paiements sont traités via Stripe, avec une sécurisation complète des transactions.","variants":["paiement sécurisé","Stripe","comment payer","sécurité paiement","payer","payement","paiement"]},
    {"id":"F27","q":"Quand le DJ reçoit-il son paiement ?","a":"Le DJ est payé après validation de l'événement, selon le modèle acompte + solde.","variants":["versement DJ","quand suis-je payé","délai paiement","recevoir argent","quand je recois","quand paiement","etre payé"]},
    {"id":"F28","q":"Que faire si mon paiement est refusé ?","a":"Vérifiez les informations de votre carte et assurez-vous que les autorisations bancaires (3D Secure) sont activées.","variants":["paiement refusé","erreur paiement","carte refusée","transaction échouée","paiement ne marche pas","carte bloquée"]},
    {"id":"F29","q":"Combien coûte l'abonnement ? Quels sont les tarifs ?","a":"CUE propose 3 formules : Starter gratuit avec 7% de commission. Pro DJ à 29€/mois avec 3% de commission, contrats IA illimités, badge Pro et priorité dans le matching. Business à 149€/mois avec 0% de commission, multi-utilisateurs et account manager dédié.","variants":["frais plateforme","commission CUE","pourcentage","tarifs","prix","abonnement","combien","cout","coût","abo","formule","plan","offre","tarif","gratuit","payant","combien ca coute","c'est combien","prix abonnement"]},
    {"id":"F30","q":"À quoi j'ai accès avec l'abonnement Pro DJ ?","a":"Avec le Pro DJ à 29€/mois vous avez : commission réduite à 3%, contrats IA illimités, badge Pro visible sur votre profil, priorité dans les résultats de matching, et analytics avancés pour suivre vos performances.","variants":["pro dj","abonnement pro","que donne le pro","accès pro","fonctionnalités pro","avec le pro","avantages pro","pro a quoi ca sert","pro dj c'est quoi"]},
    {"id":"F31","q":"Comment télécharger une facture ?","a":"Allez dans l'onglet Transactions, sélectionnez la transaction souhaitée et téléchargez le justificatif.","variants":["facture","reçu","justificatif paiement","télécharger reçu","avoir une facture"]},
    {"id":"F32","q":"Comment créer un compte sur CUE ?","a":"Cliquez sur « S'inscrire » sur la page d'accueil, entrez votre email et mot de passe, puis validez via le lien reçu par email.","variants":["inscription","s'inscrire","créer compte","nouveau compte","rejoindre CUE","m'inscrire","register","creer un compte","créer compte"]},
    {"id":"F33","q":"Qu'est-ce que CUE ?","a":"CUE est une plateforme de booking DJ qui connecte les DJs vérifiés avec les venues et organisateurs d'événements. Find. Book. Pay. Review.","variants":["c'est quoi CUE","présentation CUE","plateforme CUE","à quoi ça sert","cue c'est quoi","kézako","kesako","c est quoi"]},
    {"id":"F34","q":"Le transport est-il pris en charge ?","a":"Le transport n'est pas inclus automatiquement. Il se négocie directement entre le DJ et le venue lors de la confirmation du booking. Vous pouvez l'ajouter dans les clauses spéciales du contrat.","variants":["transport","frais de déplacement","déplacement","voyage","remboursement transport","pris en charge transport","est ce que le transport","transport payé","frais transport","deplacement","qui paye le transport"]},
    {"id":"F35","q":"Le matériel son est-il fourni par le venue ?","a":"Cela dépend du venue. Chaque venue précise dans sa fiche technique les équipements disponibles (CDJ, table de mixage, sono, éclairage). Vérifiez toujours avant de confirmer le booking.","variants":["materiel fourni","sono","equipement fourni","matos inclus","qui fournit le matos","cdj fourni","table fournie","son inclus","equip","le matos est fourni"]},
    {"id":"F36","q":"Comment laisser ou voir des avis ?","a":"Après chaque événement validé, les deux parties peuvent laisser un avis. Les avis sont visibles sur les profils DJs et venues.","variants":["avis","note","rating","évaluation","laisser avis","voir avis","noter","commentaire","review","feedback"]},
    {"id":"F37","q":"Y a-t-il une application mobile CUE ?","a":"CUE est actuellement accessible via navigateur web sur mobile et desktop. Une application native est en cours de développement.","variants":["appli","application","app","mobile","ios","android","téléphone","smartphone","app mobile"]},
    {"id":"F38","q":"Comment contacter le support CUE ?","a":"Vous pouvez nous contacter par email à cue.dj.app@gmail.com ou par téléphone au +33 7 67 01 15 32. Notre équipe répond sous 24h.","variants":["support","aide","help","contact","joindre","écrire","email support","telephone","appeler","contacter cue","service client"]},
    {"id":"F39","q":"Puis-je travailler avec CUE si je suis débutant ?","a":"Oui ! CUE accueille tous les DJs, débutants comme expérimentés. Construisez votre réputation progressivement avec des avis vérifiés.","variants":["débutant","nouveau dj","je commence","pas d'expérience","junior","debuter","novice","je suis nouveau","premier gig"]},
    {"id":"F40","q":"Comment générer un contrat de prestation ?","a":"Dans votre tableau de bord, cliquez sur « Générer un contrat », remplissez les informations (DJ, venue, date, cachet, horaires, rider) et obtenez un contrat professionnel en 30 secondes grâce à notre IA.","variants":["contrat","contrat de prestation","générer contrat","créer contrat","contrat dj","contrat ia","contrat automatique","faire un contrat"]},
]

def normalize(text: str) -> str:
    """Normalise le texte : minuscules, supprime accents et ponctuation."""
    text = text.lower()
    replacements = {
        'é':'e','è':'e','ê':'e','ë':'e',
        'à':'a','â':'a','ä':'a',
        'ù':'u','û':'u','ü':'u',
        'ô':'o','ö':'o',
        'î':'i','ï':'i',
        'ç':'c'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'[^\w\s]', ' ', text)
    return text

def search_faq(question: str, items, top_k: int = 1):
    q_norm = normalize(question)
    q_words = set(w for w in q_norm.split() if len(w) >= 2)
    scored = []

    for item in items:
        q_text = normalize(item.get("q") or "")
        a_text = normalize(item.get("a") or "")
        variants = " ".join(item.get("variants") or [])
        variants_norm = normalize(variants)
        full_text = q_text + " " + variants_norm + " " + a_text

        score = 0
        for w in q_words:
            if w in full_text:
                score += 1
            else:
                # fuzzy: cherche si le mot est contenu dans un mot du texte (tolérance typo)
                for fw in full_text.split():
                    if len(w) >= 4 and len(fw) >= 4:
                        # si 80% des caractères matchent
                        common = sum(1 for c in w if c in fw)
                        if common / max(len(w), len(fw)) >= 0.75:
                            score += 0.5
                            break

        if score > 0:
            if any(phrase in full_text for phrase in [q_norm[:20], q_norm[:15], q_norm[:10]]):
                score += 3
            scored.append((score, item))

    if not scored:
        return []

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score = scored[0][0]
    if best_score < 0.5:
        return []

    return [item for _, item in scored[:top_k]]


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

    matches = search_faq(msg, FAQ_ITEMS)

    if matches:
        best = matches[0]
        return ChatOut(
            reply=best["a"],
            sources=[best["id"]],
            escalation=False
        )

    return ChatOut(
        reply="Je n'ai pas trouvé de réponse à votre question. Contactez-nous directement : cue.dj.app@gmail.com ou +33 7 67 01 15 32 📧",
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
