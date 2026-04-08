Chat · JS
Copier

// Chatbot FAQ intelligent avec détection des fautes de frappe
 
const FAQ_DATA = [
  // ═══════════════════════════════════════════════════════════════
  // GÉNÉRAL - C'EST QUOI CUE ?
  // ═══════════════════════════════════════════════════════════════
  {
    q: "c'est quoi cue",
    variants: ["cue c'est quoi", "qu'est-ce que cue", "cue c quoi", "c koi cue", "cue kesako", "expliquez cue", "présente cue", "cue definition", "cue explication"],
    r: "CUE est LA plateforme qui connecte les DJs avec les clubs, agences, mariages et événements privés. On propose : matching IA pour trouver le DJ parfait, génération de contrats en 30 secondes, et paiements sécurisés via Stripe. Bref, on simplifie le booking DJ de A à Z ! 🎧"
  },
  {
    q: "comment ça marche",
    variants: ["comment ca fonctionne", "comment utiliser cue", "cue marche comment", "expliquez le fonctionnement", "comment faire", "ca marche comment", "fonctionnement"],
    r: "C'est simple ! 1️⃣ Créez votre profil (DJ ou Venue). 2️⃣ Utilisez notre matching IA pour trouver le partenaire idéal. 3️⃣ Générez un contrat pro en 30 secondes. 4️⃣ Paiement sécurisé via Stripe. 5️⃣ Événement validé = DJ payé. Terminé les galères ! 🚀"
  },
  {
    q: "pourquoi utiliser cue",
    variants: ["avantages cue", "pourquoi cue", "interet de cue", "cue vs autres", "benefices cue", "c'est bien cue"],
    r: "Pourquoi CUE ? ✅ Matching IA intelligent (fini les mauvaises surprises). ✅ Contrats générés en 30 sec (plus de paperasse). ✅ Paiements sécurisés Stripe (DJ payé après validation). ✅ Profils vérifiés (confiance garantie). ✅ Plateforme tout-en-un. On révolutionne le booking DJ !"
  },
 
  // ═══════════════════════════════════════════════════════════════
  // TARIFS & PRIX
  // ═══════════════════════════════════════════════════════════════
  {
    q: "combien ça coûte",
    variants: ["prix", "tarif", "tarifs", "c'est payant", "gratuit", "abonnement", "combien ca coute", "quel prix", "cout", "coût", "pricing", "free", "gratuit ou payant", "ca coute combien"],
    r: "On a 3 formules : 🆓 **Starter** : Gratuit (7% commission par booking). ⭐ **Pro DJ** : 29€/mois (3% commission + badge Pro + priorité matching). 🏢 **Business** : 149€/mois (0% commission + multi-users + API). Tu peux commencer gratuitement et upgrader quand tu veux !"
  },
  {
    q: "c'est quoi la commission",
    variants: ["commission cue", "combien de commission", "frais cue", "pourcentage cue", "cue prend combien", "frais de service"],
    r: "La commission dépend de ton plan : 🆓 Starter (gratuit) → 7% par booking. ⭐ Pro DJ (29€/mois) → 3% seulement. 🏢 Business (149€/mois) → 0% commission. Plus tu montes en gamme, moins tu paies de commission !"
  },
  {
    q: "starter c'est quoi",
    variants: ["plan starter", "formule starter", "offre gratuite", "starter gratuit"],
    r: "Le plan **Starter** c'est notre offre gratuite ! Tu as : profil DJ complet, accès au matching, paiements sécurisés, et support email. On prend juste 7% de commission quand tu décroches un booking. Parfait pour commencer ! 🎯"
  },
  {
    q: "pro dj c'est quoi",
    variants: ["plan pro", "formule pro", "offre pro", "pro dj avantages", "abonnement pro"],
    r: "Le plan **Pro DJ** à 29€/mois c'est pour les DJs sérieux ! Tu as : seulement 3% de commission, badge 'Pro' sur ton profil, priorité dans le matching IA, contrats illimités, et analytics avancés. Tu rentabilises vite ! ⭐"
  },
  {
    q: "business c'est quoi",
    variants: ["plan business", "formule business", "offre business", "entreprise", "agence"],
    r: "Le plan **Business** à 149€/mois c'est pour les agences et pros : 0% commission (!), multi-utilisateurs, accès API, et account manager dédié. Si tu fais beaucoup de bookings, c'est ultra rentable ! 🏢"
  },
 
  // ═══════════════════════════════════════════════════════════════
  // COMPTE & INSCRIPTION
  // ═══════════════════════════════════════════════════════════════
  {
    q: "comment s'inscrire",
    variants: ["inscription", "créer compte", "creer compte", "s'enregistrer", "rejoindre cue", "devenir membre", "ouvrir compte", "comment rejoindre"],
    r: "Pour t'inscrire : clique sur 'Join CUE' en haut de la page, choisis ton profil (DJ ou Venue), remplis tes infos, et c'est parti ! L'inscription est gratuite et prend 2 minutes. 🎉"
  },
  {
    q: "je n'arrive pas à me connecter",
    variants: ["connexion impossible", "login marche pas", "mot de passe oublié", "password oublié", "mdp oublié", "probleme connexion", "je peux pas me connecter", "ca marche pas login", "impossible de se connecter"],
    r: "Pas de panique ! 🔐 Vérifie ton email et mot de passe. Si tu as oublié ton mdp, clique sur 'Mot de passe oublié' sur la page de connexion. Tu recevras un email pour le réinitialiser. Toujours bloqué ? Contacte-nous : cue.dj.app@gmail.com"
  },
  {
    q: "je n'ai pas reçu l'email",
    variants: ["email pas reçu", "mail pas recu", "email de confirmation", "email validation", "pas de mail", "mail non recu", "email perdu"],
    r: "L'email joue à cache-cache ? 📧 Vérifie tes spams/courriers indésirables (on y atterrit parfois). Attends quelques minutes. Toujours rien ? Demande un renvoi depuis la page de connexion ou contacte-nous : cue.dj.app@gmail.com"
  },
  {
    q: "comment changer mon mot de passe",
    variants: ["modifier mdp", "changer mdp", "nouveau mot de passe", "reset password", "reinitialiser mdp", "modifier mot de passe"],
    r: "Pour changer ton mot de passe : va dans ton Profil → Settings → Sécurité → 'Modifier le mot de passe'. Tu peux aussi utiliser 'Mot de passe oublié' sur la page de connexion si tu ne t'en souviens plus. 🔑"
  },
  {
    q: "comment supprimer mon compte",
    variants: ["supprimer compte", "effacer compte", "fermer compte", "delete account", "désinscrire", "quitter cue"],
    r: "Tu veux nous quitter ? 😢 Va dans Settings → Confidentialité → 'Supprimer mon compte'. Attention, c'est irréversible ! Si tu as un souci, contacte-nous d'abord, on peut peut-être t'aider : cue.dj.app@gmail.com"
  },
  {
    q: "comment modifier mes infos",
    variants: ["changer infos", "modifier profil", "update profil", "mettre a jour profil", "editer profil", "changer informations"],
    r: "Pour modifier tes infos : va dans ton Dashboard → 'Mon Profil' → clique sur les champs que tu veux modifier. N'oublie pas de sauvegarder ! Tu peux changer ta bio, tes genres, tes photos, etc. ✏️"
  },
 
  // ═══════════════════════════════════════════════════════════════
  // PROFIL DJ
  // ═══════════════════════════════════════════════════════════════
  {
    q: "comment optimiser mon profil dj",
    variants: ["ameliorer profil", "profil dj conseils", "bon profil dj", "profil attractif", "plus de bookings"],
    r: "Pour un profil DJ au top : 📸 Photo pro de qualité. 🎵 Ajoute tes genres musicaux. 📝 Bio percutante (raconte ton histoire). 🎧 Liens vers tes mixes/sets. ⭐ Collecte des avis. 📅 Mets tes dispos à jour. Plus ton profil est complet, plus tu matches ! 🚀"
  },
  {
    q: "comment ajouter mes genres musicaux",
    variants: ["ajouter style", "genres musicaux", "style musical", "type de musique", "musique que je joue"],
    r: "Pour ajouter tes genres : Dashboard → Mon Profil → Section 'Genres musicaux' → sélectionne tous les styles que tu maîtrises (House, Techno, Hip-Hop, etc.). Tu peux en choisir plusieurs ! 🎵"
  },
  {
    q: "mon profil est en attente",
    variants: ["profil en attente", "validation profil", "profil pas validé", "profil en cours", "verification profil"],
    r: "Ton profil est en cours de vérification par notre équipe. Ça prend généralement quelques minutes à quelques heures. On vérifie ton identité et tes infos pour garantir la qualité sur CUE. Patience ! ⏳"
  },
  {
    q: "comment gérer mes disponibilités",
    variants: ["dispo", "disponibilités", "calendrier", "dates libres", "quand je suis dispo", "bloquer dates"],
    r: "Pour gérer tes dispos : Dashboard → Calendrier → clique sur les dates pour les marquer disponibles ou non. Les venues voient en temps réel quand tu es libre. Mets-le à jour régulièrement ! 📅"
  },
  {
    q: "c'est quoi le badge pro",
    variants: ["badge pro", "badge vérifié", "badge cue", "certification pro"],
    r: "Le badge Pro ⭐ apparaît sur ton profil quand tu as l'abonnement Pro DJ (29€/mois). Il montre aux venues que tu es un DJ sérieux et engagé. Tu apparais aussi en priorité dans les résultats de matching !"
  },
 
  // ═══════════════════════════════════════════════════════════════
  // PROFIL VENUE
  // ═══════════════════════════════════════════════════════════════
  {
    q: "comment créer un profil venue",
    variants: ["profil venue", "profil club", "profil organisateur", "inscrire venue", "inscrire club"],
    r: "Pour créer un profil Venue : clique sur 'Join CUE' → sélectionne 'I am a Venue' → remplis tes infos (nom, localisation, capacité, styles de musique, fiche technique). Les DJs pourront te trouver facilement ! 🏢"
  },
  {
    q: "c'est quoi la fiche technique",
    variants: ["fiche technique", "rider technique", "equipement", "materiel", "sono", "dj booth"],
    r: "La fiche technique décrit ton équipement : 🔊 Système son (marque, puissance). 🎛️ DJ booth (platines, mixeur). 💡 Éclairage. ⚡ Contraintes (horaires, sono à apporter). Plus c'est détaillé, mieux c'est pour les DJs !"
  },
  {
    q: "comment publier un événement",
    variants: ["creer evenement", "publier date", "chercher dj", "poster event", "nouvelle date"],
    r: "Pour publier un événement : Dashboard → 'Créer un événement' → remplis date, horaires, budget, styles recherchés, conditions. Les DJs correspondants seront notifiés et pourront postuler ! 📣"
  },
  {
    q: "comment sélectionner un dj",
    variants: ["choisir dj", "trouver dj", "selectionner dj", "quel dj choisir", "comparer dj"],
    r: "Pour choisir le bon DJ : 👀 Consulte les profils. 🎧 Écoute leurs mixes. ⭐ Lis les avis. 💬 Contacte-les via CUE. ✅ Une fois décidé, confirme le booking sur la plateforme. Notre matching IA peut aussi t'aider !"
  },
 
  // ═══════════════════════════════════════════════════════════════
  // MATCHING IA
  // ═══════════════════════════════════════════════════════════════
  {
    q: "c'est quoi le matching ia",
    variants: ["matching", "ia matching", "intelligence artificielle", "algorithme", "trouver dj automatique", "matching cue"],
    r: "Notre matching IA analyse ton événement (type, vibe, budget, lieu) et te propose les DJs les plus compatibles avec un score de match. Plus besoin de chercher pendant des heures, on fait le travail pour toi ! 🎯🤖"
  },
  {
    q: "comment utiliser le matching",
    variants: ["utiliser matching", "lancer matching", "faire matching", "matching comment"],
    r: "Super simple ! Va dans la section 'Find a DJ' → décris ton événement (type, ambiance, budget, ville) → clique sur 'Find DJs' → notre IA te propose les meilleurs profils avec leur score de compatibilité. Magic ! ✨"
  },
  {
    q: "le matching est fiable",
    variants: ["matching fiable", "matching precis", "matching marche bien", "confiance matching"],
    r: "Notre matching analyse plein de critères : genres musicaux, expérience, avis, localisation, budget, style... Plus tu donnes de détails, plus c'est précis. On a 90%+ de satisfaction sur les matchs ! 🎯"
  },
 
  // ═══════════════════════════════════════════════════════════════
  // CONTRATS
  // ═══════════════════════════════════════════════════════════════
  {
    q: "comment générer un contrat",
    variants: ["creer contrat", "faire contrat", "contrat dj", "generer contrat", "contrat automatique"],
    r: "Générer un contrat prend 30 secondes ! Va dans 'Generate Contract' → remplis : nom DJ, venue, date, horaires, cachet, rider technique → clique sur 'Generate'. Tu obtiens un contrat pro en 10 sections, prêt à signer ! 📋"
  },
  {
    q: "c'est quoi dans le contrat",
    variants: ["contenu contrat", "sections contrat", "contrat contient quoi", "modele contrat"],
    r: "Nos contrats incluent 10 sections : 1️⃣ Parties 2️⃣ Objet 3️⃣ Date/Horaires 4️⃣ Rémunération 5️⃣ Rider technique 6️⃣ Obligations venue 7️⃣ Obligations DJ 8️⃣ Annulation 9️⃣ Clauses particulières 🔟 Signatures. Tout est carré !"
  },
  {
    q: "le contrat est légal",
    variants: ["contrat valide", "contrat legal", "contrat juridique", "valeur legale contrat"],
    r: "Nos contrats sont rédigés selon les standards juridiques français pour les prestations artistiques. Ils ont valeur légale une fois signés par les deux parties. Pour des cas complexes, on conseille toujours de consulter un avocat. ⚖️"
  },
  {
    q: "c'est quoi le rider technique",
    variants: ["rider", "rider dj", "technical rider", "fiche technique dj"],
    r: "Le rider technique liste ce dont le DJ a besoin : 🎛️ Platines (CDJ, vinyles). 🎚️ Table de mixage. 🎧 Monitoring. 🔌 Branchements. Tu peux le spécifier dans le contrat pour éviter les mauvaises surprises le jour J !"
  },
 
  // ═══════════════════════════════════════════════════════════════
  // BOOKING & RÉSERVATION
  // ═══════════════════════════════════════════════════════════════
  {
    q: "comment fonctionne un booking",
    variants: ["booking comment", "reservation comment", "processus booking", "etapes booking"],
    r: "Le processus booking : 1️⃣ Demande envoyée 2️⃣ DJ accepte 3️⃣ Paiement sécurisé (acompte) 4️⃣ Contrat signé 5️⃣ Événement 6️⃣ Venue valide la prestation 7️⃣ DJ reçoit le paiement. Tout est tracé et sécurisé ! ✅"
  },
  {
    q: "comment annuler un booking",
    variants: ["annuler booking", "annuler reservation", "cancel booking", "annulation"],
    r: "Pour annuler : va dans 'Mes Bookings' → sélectionne le booking → 'Annuler'. Attention aux conditions d'annulation définies dans le contrat ! Selon le délai, l'acompte peut être conservé ou remboursé. 📝"
  },
  {
    q: "je peux modifier un booking",
    variants: ["modifier booking", "changer booking", "modifier reservation", "changer date booking"],
    r: "Tu peux modifier un booking (date, horaires, cachet) mais les modifications doivent être validées par les deux parties. Tout se fait via la messagerie CUE pour garder une trace. On reste transparents ! 🤝"
  },
  {
    q: "que faire si le dj ne vient pas",
    variants: ["dj absent", "no show", "dj vient pas", "dj annule", "dj pas venu"],
    r: "Si le DJ ne se présente pas (no-show) : signale-le immédiatement depuis le booking. On ouvre un dossier, tu es remboursé, et le DJ est sanctionné. C'est pour ça qu'on vérifie tous les profils ! 🚨"
  },
  {
    q: "comment contacter le dj ou la venue",
    variants: ["contacter dj", "contacter venue", "messagerie", "envoyer message", "chat dj"],
    r: "Utilise uniquement le chat intégré CUE pour communiquer. Ça permet de garder une trace officielle en cas de litige. Tu le trouves dans chaque booking. Pas d'échanges hors plateforme ! 💬"
  },
 
  // ═══════════════════════════════════════════════════════════════
  // PAIEMENTS
  // ═══════════════════════════════════════════════════════════════
  {
    q: "comment sont sécurisés les paiements",
    variants: ["paiement securisé", "securite paiement", "stripe", "paiement safe", "protection paiement"],
    r: "Les paiements passent par **Stripe**, leader mondial du paiement sécurisé. 🔒 Ton argent est protégé jusqu'à validation de l'événement. Le DJ est payé seulement après que la venue confirme la prestation. Zéro risque !"
  },
  {
    q: "quand le dj est payé",
    variants: ["paiement dj quand", "dj reçoit argent", "virement dj", "dj paye quand"],
    r: "Le DJ est payé en 2 temps : 💰 Acompte (50%) à la signature du contrat. 💰 Solde (50%) après validation de la prestation par la venue. Le virement arrive sous 2-5 jours ouvrés après validation."
  },
  {
    q: "mon paiement est refusé",
    variants: ["paiement refuse", "carte refusee", "paiement marche pas", "erreur paiement"],
    r: "Paiement refusé ? Vérifie : 💳 Numéro de carte correct. 📅 Date d'expiration valide. 🔐 3D Secure activé sur ta carte. 💶 Solde suffisant. Si ça persiste, essaie une autre carte ou contacte ta banque."
  },
  {
    q: "comment télécharger une facture",
    variants: ["facture", "telecharger facture", "obtenir facture", "facture booking"],
    r: "Pour tes factures : Dashboard → 'Paiements' ou 'Transactions' → sélectionne la transaction → 'Télécharger le justificatif'. Tu peux télécharger en PDF pour ta compta ! 🧾"
  },
  {
    q: "remboursement comment ça marche",
    variants: ["remboursement", "etre rembourse", "recuperer argent", "rembourser"],
    r: "Les remboursements sont traités selon les conditions du contrat. En cas d'annulation par la venue ou no-show DJ, tu es remboursé automatiquement. Délai : 5-10 jours ouvrés sur ta carte. Pour tout litige, contacte-nous ! 💸"
  },
 
  // ═══════════════════════════════════════════════════════════════
  // SÉCURITÉ & VÉRIFICATION
  // ═══════════════════════════════════════════════════════════════
  {
    q: "mes données sont sécurisées",
    variants: ["securite donnees", "donnees protegees", "privacy", "vie privee", "rgpd", "donnees personnelles"],
    r: "Tes données sont en sécurité ! 🔒 On utilise le chiffrement SSL, on respecte le RGPD, et on ne partage jamais tes infos sans ton accord. Tes données de paiement sont gérées par Stripe (pas stockées chez nous)."
  },
  {
    q: "pourquoi vérifier mon identité",
    variants: ["verification identite", "pourquoi verifier", "kyc", "verification compte"],
    r: "La vérification d'identité protège tout le monde ! ✅ Elle garantit que les DJs sont de vraies personnes. ✅ Elle sécurise les paiements. ✅ Elle renforce la confiance sur la plateforme. C'est rapide et confidentiel."
  },
  {
    q: "combien de temps la vérification",
    variants: ["verification combien temps", "duree verification", "temps verification"],
    r: "La vérification prend généralement quelques minutes (automatique). Parfois, un contrôle manuel peut prendre jusqu'à 24-48h si on a besoin de vérifs supplémentaires. On te notifie dès que c'est fait ! ⏳"
  },
  {
    q: "ma vérification est refusée",
    variants: ["verification refusee", "verification echouee", "documents refuses"],
    r: "Vérification refusée ? Vérifie que : 📸 La photo est nette et lisible. 📄 Le document est valide (non expiré). 🔍 Les infos correspondent à ton profil. Réessaie avec de meilleurs documents ou contacte-nous !"
  },
  {
    q: "comment signaler un problème",
    variants: ["signaler", "signaler probleme", "signaler abus", "report", "comportement suspect"],
    r: "Pour signaler un souci : va sur le profil ou le booking concerné → clique sur 'Signaler' (🚩). Décris le problème. Notre équipe examine chaque signalement sous 24h. On prend ça très au sérieux ! 🛡️"
  },
 
  // ═══════════════════════════════════════════════════════════════
  // AVIS & RÉPUTATION
  // ═══════════════════════════════════════════════════════════════
  {
    q: "comment fonctionnent les avis",
    variants: ["avis", "reviews", "notes", "evaluer dj", "notation"],
    r: "Après chaque booking validé, DJ et Venue peuvent se noter mutuellement (1-5 étoiles + commentaire). Seuls les avis de vrais bookings comptent, pas de faux avis possibles ! Ça construit ta réputation. ⭐"
  },
  {
    q: "comment avoir de bons avis",
    variants: ["bons avis", "ameliorer avis", "meilleurs avis", "plus d'etoiles"],
    r: "Pour avoir de bons avis : 🎵 Assure une super prestation. ⏰ Sois ponctuel. 💬 Communique bien. 🎧 Respecte le brief. 😊 Sois pro et sympa. Les bons avis viennent naturellement quand tu fais du bon travail !"
  },
  {
    q: "je peux supprimer un avis",
    variants: ["supprimer avis", "effacer avis", "retirer avis", "avis negatif"],
    r: "Les avis ne peuvent pas être supprimés (sauf s'ils violent nos règles : insultes, fausses infos...). Tu peux répondre publiquement à un avis négatif pour donner ta version. C'est la transparence ! 📝"
  },
 
  // ═══════════════════════════════════════════════════════════════
  // SUPPORT & CONTACT
  // ═══════════════════════════════════════════════════════════════
  {
    q: "comment contacter cue",
    variants: ["contact cue", "support cue", "aide cue", "email cue", "joindre cue", "service client"],
    r: "Tu peux nous contacter : 📧 Email : cue.dj.app@gmail.com. 💬 Ce chat (je suis là !). 📱 Réseaux : @cuedjapp. On répond généralement sous 24h. N'hésite pas ! 🙋"
  },
  {
    q: "j'ai un problème",
    variants: ["probleme", "aide", "help", "sos", "besoin d'aide", "ca marche pas", "bug"],
    r: "Pas de panique, je suis là pour t'aider ! 🙋 Décris-moi ton problème précisément et je ferai de mon mieux. Si c'est technique, tu peux aussi écrire à cue.dj.app@gmail.com avec des screenshots."
  },
  {
    q: "merci",
    variants: ["merci beaucoup", "thanks", "thank you", "cool merci", "ok merci", "super merci", "parfait merci"],
    r: "Avec plaisir ! 😊 Si tu as d'autres questions, je suis là. Bonne continuation sur CUE ! 🎧🎉"
  },
  {
    q: "bonjour",
    variants: ["salut", "hello", "hey", "coucou", "yo", "bonsoir", "hi", "bjr", "slt"],
    r: "Hey ! 👋 Bienvenue sur CUE ! Je suis MAX, ton assistant. Comment je peux t'aider aujourd'hui ? 🎧"
  },
  {
    q: "au revoir",
    variants: ["bye", "goodbye", "a plus", "ciao", "à bientôt", "bonne journée", "bonne soirée"],
    r: "À bientôt ! 👋 N'hésite pas si tu as d'autres questions. Bonne continuation sur CUE ! 🎧🎉"
  }
];
 
// ═══════════════════════════════════════════════════════════════
// FONCTION DE SIMILARITÉ (détecte les fautes de frappe)
// ═══════════════════════════════════════════════════════════════
function levenshtein(a, b) {
  const matrix = [];
  for (let i = 0; i <= b.length; i++) matrix[i] = [i];
  for (let j = 0; j <= a.length; j++) matrix[0][j] = j;
  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }
  return matrix[b.length][a.length];
}
 
function similarity(s1, s2) {
  const longer = s1.length > s2.length ? s1 : s2;
  const shorter = s1.length > s2.length ? s2 : s1;
  if (longer.length === 0) return 1.0;
  return (longer.length - levenshtein(longer, shorter)) / longer.length;
}
 
function normalize(text) {
  return text
    .toLowerCase()
    .normalize("NFD").replace(/[\u0300-\u036f]/g, "") // Enlève accents
    .replace(/[^a-z0-9\s]/g, " ") // Enlève ponctuation
    .replace(/\s+/g, " ")
    .trim();
}
 
function searchFaq(question) {
  const normalizedQ = normalize(question);
  const words = normalizedQ.split(" ").filter(w => w.length > 1);
  
  let bestMatch = null;
  let bestScore = 0;
 
  for (const item of FAQ_DATA) {
    let score = 0;
    
    // Cherche dans la question principale
    const normalizedItemQ = normalize(item.q);
    
    // Score de similarité globale
    const globalSim = similarity(normalizedQ, normalizedItemQ);
    score += globalSim * 50;
    
    // Cherche dans les variants
    for (const variant of item.variants || []) {
      const normalizedVariant = normalize(variant);
      const variantSim = similarity(normalizedQ, normalizedVariant);
      if (variantSim > 0.7) score += variantSim * 40;
      
      // Correspondance exacte d'un variant
      if (normalizedQ.includes(normalizedVariant) || normalizedVariant.includes(normalizedQ)) {
        score += 30;
      }
    }
    
    // Score par mots-clés (avec tolérance aux fautes)
    const itemWords = normalize(item.q + " " + (item.variants || []).join(" ")).split(" ");
    for (const word of words) {
      for (const itemWord of itemWords) {
        if (word === itemWord) {
          score += 15; // Mot exact
        } else if (word.length > 3 && itemWord.length > 3) {
          const wordSim = similarity(word, itemWord);
          if (wordSim > 0.75) {
            score += wordSim * 10; // Mot similaire (faute de frappe)
          }
        }
      }
    }
    
    if (score > bestScore) {
      bestScore = score;
      bestMatch = item;
    }
  }
 
  // Seuil minimum pour retourner une réponse
  return bestScore > 15 ? bestMatch : null;
}
 
// ═══════════════════════════════════════════════════════════════
// HANDLER NETLIFY
// ═══════════════════════════════════════════════════════════════
exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
  };
 
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }
 
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers, body: JSON.stringify({ detail: 'Method not allowed' }) };
  }
 
  try {
    const { message } = JSON.parse(event.body);
    
    if (!message || !message.trim()) {
      return { statusCode: 400, headers, body: JSON.stringify({ detail: 'Empty message.' }) };
    }
 
    const match = searchFaq(message);
    
    if (match) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          reply: match.r,
          sources: [],
          escalation: false
        })
      };
    }
 
    // Pas de match trouvé
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        reply: "Hmm, je n'ai pas trouvé de réponse précise à ta question. 🤔 Essaie de reformuler ou contacte-nous directement : cue.dj.app@gmail.com — on répond vite ! 📧",
        sources: [],
        escalation: true
      })
    };
 
  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ detail: error.message })
    };
  }
};
