
// ══════════════════════════════════════════════════════
// CONFIG — ⚠️ Changez cette URL avant de déployer en production
// ══════════════════════════════════════════════════════
const API_BASE = 'https://cue-backend-c1x8.onrender.com';

// ══════════════════════════════════════════════════════
// AUTH
// ══════════════════════════════════════════════════════
let currentUser = null, selectedRole = null;
const USERS = [{email:'stanislas.kleb@outlook.com', pass:'Stan131234', roles:['dj','venue'], name:'Stanislas Kleb'}];

function openAuth(){document.getElementById('authOverlay').classList.remove('hidden');}
function openAuthAs(role){selectRole(role);openAuth();}
function closeAuth(){document.getElementById('authOverlay').classList.add('hidden');selectedRole=null;resetAuthSteps();}
function resetAuthSteps(){
  document.getElementById('stepRole').style.display='block';
  document.getElementById('stepLogin').style.display='none';
  document.getElementById('optDJ').classList.remove('sel');
  document.getElementById('optVenue').classList.remove('sel');
  document.getElementById('loginErr').classList.remove('on');
  document.getElementById('loginSpin').style.display='none';
  document.getElementById('loginLabel').textContent='SE CONNECTER →';
}
function selectRole(role){
  selectedRole=role;
  document.getElementById('optDJ').classList.toggle('sel',role==='dj');
  document.getElementById('optVenue').classList.toggle('sel',role==='venue');
  document.getElementById('roleTag').textContent=role==='dj'?'🎧 DJ Login':'🏢 Venue Login';
  document.getElementById('stepRole').style.display='none';
  document.getElementById('stepLogin').style.display='block';
  setTimeout(()=>document.getElementById('loginEmail').focus(),80);
}
function backToRole(){
  document.getElementById('stepRole').style.display='block';
  document.getElementById('stepLogin').style.display='none';
}
function doLogin(){
  const email=document.getElementById('loginEmail').value.trim().toLowerCase();
  const pass=document.getElementById('loginPassword').value;
  const user=USERS.find(u=>u.email===email&&u.pass===pass&&u.roles.includes(selectedRole));
  if(!user){document.getElementById('loginErr').classList.add('on');return;}
  currentUser=user;
  document.getElementById('authOverlay').classList.add('hidden');
  resetAuthSteps();
  if(selectedRole==='dj'){
    document.getElementById('dashDJ').classList.add('active');
    document.getElementById('mainSite').style.display='none';
    document.getElementById('djName').textContent=user.name;
    document.getElementById('djAvatar').textContent=user.name[0].toUpperCase();
  } else {
    document.getElementById('dashVenue').classList.add('active');
    document.getElementById('mainSite').style.display='none';
    document.getElementById('venueName').textContent=user.name;
    document.getElementById('venueAvatar').textContent=user.name[0].toUpperCase();
  }
  document.getElementById('navCta').innerHTML=`<button class="logout-btn" onclick="logout()">Logout</button>`;
  window.scrollTo(0,0);
}
function logout(){
  currentUser=null;selectedRole=null;
  document.getElementById('dashDJ').classList.remove('active');
  document.getElementById('dashVenue').classList.remove('active');
  document.getElementById('mainSite').style.display='block';
  document.getElementById('navCta').innerHTML=`<button class="bg" onclick="openAuth()">Login</button><button class="bp" onclick="openAuth()">Join CUE</button>`;
  window.scrollTo(0,0);
}
function goHome(){
  document.getElementById('dashDJ').classList.remove('active');
  document.getElementById('dashVenue').classList.remove('active');
  document.getElementById('mainSite').style.display='block';
  window.scrollTo(0,0);
}
function scrollToMatching(){goHome();setTimeout(()=>document.getElementById('matching').scrollIntoView({behavior:'smooth'}),100);}
function scrollToContract(){goHome();setTimeout(()=>document.getElementById('contracts').scrollIntoView({behavior:'smooth'}),100);}

// ══════════════════════════════════════════════════════
// NAV SCROLL
// ══════════════════════════════════════════════════════
window.addEventListener('scroll',()=>document.getElementById('nav').classList.toggle('s',scrollY>50));

// ══════════════════════════════════════════════════════
// AI MATCHING — FIX: code orphelin supprimé, une seule fonction propre
// ══════════════════════════════════════════════════════
async function runMatching(){
  const btn=document.getElementById('matchBtn');
  const spin=document.getElementById('matchSpin');
  const lab=document.getElementById('matchLabel');
  const out=document.getElementById('matchResults');

  btn.disabled=true;
  spin.classList.add('on');
  lab.textContent='Searching...';
  out.innerHTML='<div class="result-placeholder"><div class="result-placeholder-icon pulsing">🎧</div><div class="result-placeholder-text pulsing">Analysing...</div></div>';

  const payload={
    type:document.getElementById('evType').value,
    vibe:document.getElementById('evVibe').value||'Non précisé',
    budget:document.getElementById('evBudget').value,
    city:document.getElementById('evCity').value||'Non précisée',
    details:document.getElementById('evDetails').value||'Aucun'
  };

  try{
    const res=await fetch(`${API_BASE}/match`,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(payload)
    });
    const data=await res.json();
    if(!res.ok) throw new Error(data.detail||'Erreur serveur');
    const djs=data.djs;
    out.innerHTML='<div class="dj-results">'+djs.map(d=>`
      <div class="dj-card">
        <div class="dj-avatar">${d.name.split(' ').map(w=>w[0]).join('').slice(0,2)}</div>
        <div style="flex:1">
          <div class="dj-name">${d.name}</div>
          <div class="dj-tags">${d.tags.map(t=>`<span class="dj-tag y">${t}</span>`).join('')}<span class="dj-tag">${d.price}</span></div>
          <div class="dj-desc">${d.bio}</div>
        </div>
        <div style="text-align:right;flex-shrink:0">
          <div class="dj-match">${d.match}%</div>
          <div class="dj-match-label">Match</div>
          <button class="bp" style="margin-top:10px;padding:6px 14px;font-size:11px" onclick="openAuth()">BOOK</button>
        </div>
      </div>`).join('')+'</div>';
  }catch(e){
    out.innerHTML=`<div class="result-placeholder"><div class="result-placeholder-text" style="color:#ff4444;opacity:1">❌ ${e.message}</div></div>`;
  }
  btn.disabled=false;
  spin.classList.remove('on');
  lab.textContent='⚡ FIND DJs →';
}

// ══════════════════════════════════════════════════════
// CONTRACT GENERATOR — FIX: code orphelin supprimé, une seule fonction propre
// ══════════════════════════════════════════════════════
let contractText='';
async function runContract(){
  const dj=document.getElementById('cDJ').value.trim();
  const venue=document.getElementById('cVenue').value.trim();
  if(!dj||!venue){alert('Le nom du DJ et du Venue sont requis.');return;}

  const btn=document.getElementById('contractBtn');
  const spin=document.getElementById('contractSpin');
  const lab=document.getElementById('contractLabel');
  const out=document.getElementById('contractOutput');
  const toolbar=document.getElementById('contractToolbar');

  btn.disabled=true;
  spin.classList.add('on');
  lab.textContent='Generating...';
  toolbar.style.display='none';
  out.innerHTML='<div style="text-align:center;padding:40px;color:var(--MUTED)" class="pulsing">⚡ Génération du contrat en cours...</div>';

  const payload={
    dj,
    venue,
    date:document.getElementById('cDate').value,
    start:document.getElementById('cStart').value,
    end:document.getElementById('cEnd').value,
    fee:parseFloat(document.getElementById('cFee').value)||0,
    rider:document.getElementById('cRider').value,
    clauses:document.getElementById('cClauses').value
  };

  try{
    const res=await fetch(`${API_BASE}/contract`,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(payload)
    });
    const data=await res.json();
    if(!res.ok) throw new Error(data.detail||'Erreur serveur');

    contractText=data.contract_text;
    const text=contractText;

    const dj=document.getElementById('cDJ').value.trim();
    const venue=document.getElementById('cVenue').value.trim();
    const dateVal=document.getElementById('cDate').value;
    const feeVal=document.getElementById('cFee').value;
    const startVal=document.getElementById('cStart').value;
    const endVal=document.getElementById('cEnd').value;
    const today=new Date().toLocaleDateString('en-GB',{day:'2-digit',month:'long',year:'numeric'});

    let html='<div class="contract-header-bar">'
      +'<div><div class="contract-logo">CUE</div>'
      +'<div style="font-size:9px;color:rgba(0,0,0,.5);letter-spacing:1px;text-transform:uppercase;margin-top:2px">DJ Performance Contract</div></div>'
      +'<div style="text-align:right">'
      +'<div style="font-size:10px;color:#000;font-weight:700">'+dj+' x '+venue+'</div>'
      +'<div style="font-size:9px;color:rgba(0,0,0,.5);margin-top:2px">'+(dateVal||'Date TBC')+' - '+startVal+' to '+endVal+(feeVal?' - '+feeVal+'eu':'')+'</div>'
      +'</div></div><div class="contract-inner">';
    var re=/###SECTION_(\d+):\s*([^#]+)###([\s\S]*?)(?=###SECTION_|\s*$)/g;
    var m,found=false;
    while((m=re.exec(text))!==null){
      found=true;
      html+='<div class="section-block">'
        +'<div class="section-title"><span class="sec-num">'+m[1].trim()+'</span>'+m[2].trim()+'</div>'
        +'<p>'+m[3].trim().replace(/\n/g,'<br>')+'</p>'
        +'</div>';
    }
    if(!found) html+='<p>'+text.replace(/\n/g,'<br>')+'</p>';
    html+='</div><div class="contract-footer-bar">'
      +'<span>Generated by CUE AI - '+today+'</span>'
      +'<span style="color:#FFC300">OFFICIAL DOCUMENT</span>'
      +'</div>';
    out.innerHTML=html;
    toolbar.style.display='flex';
  }catch(e){
    out.innerHTML=`<div style="padding:20px;color:#ff4444">❌ ${e.message}</div>`;
  }
  btn.disabled=false;
  spin.classList.remove('on');
  lab.textContent='📋 GENERATE CONTRACT →';
}

function copyContract(){
  navigator.clipboard?.writeText(contractText);
  const btn=document.getElementById('copyBtn');
  btn.textContent='✓ Copied!';btn.style.color='#00c864';
  setTimeout(()=>{btn.textContent='📋 Copy';btn.style.color='';},2000);
}

// ══════════════════════════════════════════════════════
// CHATBOT
// ══════════════════════════════════════════════════════
let chatOpen=false,chatHist=[];

function toggleChat(){
  chatOpen=!chatOpen;
  document.getElementById('cwin').classList.toggle('open',chatOpen);
  if(chatOpen)document.getElementById('cinput').focus();
}
function addCMsg(t,r){
  const e=document.createElement('div');e.className='cmsg '+r;
  if(r==='bot')e.style.whiteSpace='pre-line';
  e.textContent=t;
  const m=document.getElementById('cmsgs');m.appendChild(e);m.scrollTop=m.scrollHeight;
  return e;
}
function addTyping(){
  const e=document.createElement('div');e.className='cmsg typing';e.id='ctyp';
  e.innerHTML='<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
  const m=document.getElementById('cmsgs');m.appendChild(e);m.scrollTop=m.scrollHeight;
}
function rmTyping(){document.getElementById('ctyp')?.remove();}

async function sendChat(){
  const i=document.getElementById('cinput');
  const msg=i.value.trim();
  if(!msg)return;
  i.value='';
  document.getElementById('csend').disabled=true;
  addCMsg(msg,'user');
  chatHist.push({role:'user',content:msg});
  addTyping();
  try{
    const res=await fetch(`${API_BASE}/chat`,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message:msg})
    });
    const d=await res.json();
    if(!res.ok) throw new Error(d.detail||`Erreur ${res.status}`);
    const rep=d.reply||'Désolé, une erreur est survenue.';
    rmTyping();
    addCMsg(rep,'bot');
    chatHist.push({role:'assistant',content:rep});
  }catch(e){
    rmTyping();
    addCMsg(`❌ ${e.message}`,'bot');
  }
  document.getElementById('csend').disabled=false;
  i.focus();
}

// ══════════════════════════════════════════════════════
// MODERATOR
// ══════════════════════════════════════════════════════
let FAQ_DATA=[
  {q:"Je ne parviens pas à me connecter",r:"Vérifiez votre email et mot de passe. Utilisez « Password oublié » si nécessaire."},
  {q:"Je n'ai pas reçu l'email de validation",r:"Vérifiez vos courriers indésirables. Renvoyez l'email depuis la page de connexion."},
  {q:"Comment réinitialiser mon mot de passe ?",r:"Cliquez sur « Password oublié », entrez votre email et suivez les instructions."},
  {q:"Comment modifier mes informations personnelles ?",r:"Profil → Settings → Edit les informations."},
  {q:"Comment supprimer mon compte ?",r:"Settings → Confidentialité → Supprimer mon compte."},
  {q:"Pourquoi vérifier mon identité ?",r:"La vérification sécurise les transactions et assure la fiabilité des utilisateurs."},
  {q:"Combien de temps prend la vérification ?",r:"Quelques minutes en général. Un contrôle manuel peut parfois prolonger le délai."},
  {q:"Ma vérification est refusée, que faire ?",r:"Vérifiez la qualité et validité de vos documents, puis soumettez à nouveau."},
  {q:"Mes données sont-elles sécurisées ?",r:"Oui. CUE chiffre toutes les données sensibles et applique des standards de sécurité élevés."},
  {q:"Comment signaler un comportement suspect ?",r:"Bouton « Signaler » sur le profil ou dans le booking concerné."},
  {q:"Comment optimiser mon profil DJ ?",r:"Ajoutez biographie, genres musicaux, références, extraits audio et disponibilités."},
  {q:"Puis-je sélectionner plusieurs styles musicaux ?",r:"Oui, assurez-vous qu'ils correspondent à votre univers artistique."},
  {q:"Comment augmenter mes chances d'être sélectionné ?",r:"Profil complet, avis positifs, et respect de vos engagements."},
  {q:"My profile est en attente de validation",r:"Une vérification qualité est en cours. Cela prend généralement quelques minutes."},
  {q:"Comment gérer mes disponibilités ?",r:"Tableau de bord → section Calendrier → mettez à jour vos dates."},
  {q:"Comment créer un profil venue ?",r:"Sélectionnez « Venue » à l'inscription, complétez : localisation, capacité, styles et fiche technique."},
  {q:"Comment préciser les équipements disponibles ?",r:"Dans la fiche technique : audio, DJ booth, éclairage et contraintes horaires."},
  {q:"Comment publier une date à pourvoir ?",r:"« Créer un événement » → date, budget, styles, conditions."},
  {q:"Comment sélectionner un DJ ?",r:"Consultez les profils, écoutez les extraits, vérifiez les avis, confirmez via la plateforme."},
  {q:"Puis-je modifier un événement publié ?",r:"Oui, tant qu'il n'est pas confirmé par un DJ."},
  {q:"Comment fonctionne un booking sur CUE ?",r:"Demande → Acceptation → Paiement sécurisé → Confirmation → Événement → Validation → Évaluation."},
  {q:"Puis-je modifier un booking confirmé ?",r:"Oui, mais les modifications doivent être validées par les deux parties."},
  {q:"Que faire en cas de no-show ?",r:"Signalez immédiatement depuis le booking pour ouverture d'un dossier."},
  {q:"Comment contacter l'autre partie ?",r:"Via le chat intégré CUE uniquement, pour conserver une trace officielle."},
  {q:"Puis-je annuler un booking ?",r:"Oui, selon les conditions d'annulation définies à la confirmation."},
  {q:"Comment les paiements sont-ils sécurisés ?",r:"Via Stripe, avec sécurisation complète des transactions."},
  {q:"Quand le DJ reçoit-il son paiement ?",r:"Après validation de l'événement (modèle acompte + solde)."},
  {q:"Que faire si mon paiement est refusé ?",r:"Vérifiez votre carte et les autorisations bancaires (3D Secure)."},
  {q:"Quelle commission CUE applique-t-elle ?",r:"Starter : gratuit 7%. Pro DJ : 29€/mois 3%. Business : 149€/mois 0%."},
  {q:"Comment télécharger une facture ?",r:"Onglet Transactions → sélectionnez la transaction → téléchargez le justificatif."},
];

function showModoLogin(){document.getElementById('modoLoginWrap').classList.remove('hidden');}
function hideModoLogin(){document.getElementById('modoLoginWrap').classList.add('hidden');}
function modoLogin(){
  const email=document.getElementById('modoEmail').value.trim().toLowerCase();
  const pass=document.getElementById('modoPass').value;
  const err=document.getElementById('modoErr');err.style.display='none';
  if(email!=='stanislas.kleb@outlook.com'||pass!=='Stan131234'){err.style.display='block';return;}
  hideModoLogin();
  document.getElementById('modoDash').classList.add('open');
  renderFAQEditor();
}
function modoLogout(){document.getElementById('modoDash').classList.remove('open');}
function switchMTab(el,sec){
  document.querySelectorAll('.mtab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.msec').forEach(s=>s.classList.remove('active'));
  el.classList.add('active');
  document.getElementById(sec).classList.add('active');
}
function renderFAQEditor(){
  const c=document.getElementById('faqEditorContainer');
  c.innerHTML=FAQ_DATA.map((f,i)=>`
    <div class="faq-item">
      <div class="faq-q" onclick="toggleFaqItem(${i})">
        <span><span class="faq-q-num">${String(i+1).padStart(2,'0')}.</span><span class="faq-q-text">${f.q}</span></span>
        <span id="faq-arr-${i}" style="color:#333;fo