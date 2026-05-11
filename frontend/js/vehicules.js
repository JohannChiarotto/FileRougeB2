/**
 * vehicules.js — Logique de la page catalogue véhicules
 * Gère filtres, pagination, affichage des cards et modal détail.
 */

/* ── État de la page ─────────────────────────────────────── */
const state = {
  page:    1,
  perPage: 12,
  total:   0,
  etat:    "",
  sort:    "created_at_desc",
  filters: {
    q:        "",
    energie:  "",
    agence_id:"",
    annee_min:"",
    prix_max: null,
    km_max:   null,
  },
};

/* ── Utilitaires ─────────────────────────────────────────── */
const fmt = {
  prix:  (n) => new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n),
  km:    (n) => new Intl.NumberFormat("fr-FR").format(n) + " km",
  num:   (n) => new Intl.NumberFormat("fr-FR").format(n),
};

const energieLabel = {
  essence:              "Essence",
  diesel:               "Diesel",
  electrique:           "Électrique",
  hybride:              "Hybride",
  hybride_rechargeable: "Hybride Plug-in",
  gpl:                  "GPL",
};

/* ── Chargement initial ──────────────────────────────────── */
document.addEventListener("DOMContentLoaded", async () => {
  await loadAgences();
  populateAnneesFilter();
  await loadVehicules();
  bindEvents();
  Api.helpers.updateNavAuth();
});

/* ── Charger les agences dans le select ─────────────────── */
async function loadAgences() {
  try {
    const agences = await Api.agences.list();
    const sel = document.getElementById("filter-agence");
    agences.forEach(a => {
      const opt = document.createElement("option");
      opt.value = a.id;
      opt.textContent = a.ville + (a.est_siege ? " ★" : "");
      sel.appendChild(opt);
    });
  } catch (e) {
    console.warn("Impossible de charger les agences", e);
  }
}

/* ── Remplir les années ─────────────────────────────────── */
function populateAnneesFilter() {
  const sel = document.getElementById("filter-annee");
  const currentYear = new Date().getFullYear();
  for (let y = currentYear; y >= 2005; y--) {
    const opt = document.createElement("option");
    opt.value = y; opt.textContent = y;
    sel.appendChild(opt);
  }
}

/* ── Charger et afficher les véhicules ───────────────────── */
async function loadVehicules() {
  const grid = document.getElementById("vehicules-grid");
  grid.innerHTML = `<div class="grid-loader"><div class="loader-spinner"></div><p>Chargement…</p></div>`;

  try {
    const params = {
      page:     state.page,
      per_page: state.perPage,
      sort:     state.sort,
      statut:   "disponible",
      ...state.filters,
    };
    if (state.etat) params.etat = state.etat;

    const data = await Api.vehicules.list(params);
    state.total = data.total;

    // Résultats
    document.getElementById("results-count").textContent =
      `${fmt.num(data.total)} véhicule${data.total > 1 ? "s" : ""} trouvé${data.total > 1 ? "s" : ""}`;

    if (data.items.length === 0) {
      grid.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">🚗</div>
          <h3>Aucun véhicule trouvé</h3>
          <p>Essayez de modifier vos filtres de recherche.</p>
        </div>`;
      document.getElementById("pagination").innerHTML = "";
      return;
    }

    grid.innerHTML = data.items.map(renderCard).join("");

    // Listener sur chaque card
    grid.querySelectorAll(".vehicle-card").forEach(card => {
      card.addEventListener("click", () => openModal(card.dataset.uuid));
    });

    renderPagination(data.pages);

  } catch (err) {
    grid.innerHTML = `<div class="empty-state"><p style="color:var(--red)">Erreur : ${err.message}</p></div>`;
  }
}

/* ── Rendu d'une card ────────────────────────────────────── */
function renderCard(v) {
  const img = v.photo
    ? `<img class="card-img" src="${v.photo}" alt="${v.marque} ${v.modele}" loading="lazy"/>`
    : `<div class="card-img-placeholder"><svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="1"><rect x="1" y="6" width="22" height="12" rx="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/></svg></div>`;

  const prixBarre = v.prix_barre
    ? `<div class="card-prix-barre">${fmt.prix(v.prix_barre)}</div>` : "";

  return `
    <article class="vehicle-card" data-uuid="${v.uuid}" role="button" tabindex="0" aria-label="${v.marque} ${v.modele} ${v.annee}">
      <span class="card-badge ${v.etat}">${v.etat === "neuf" ? "Neuf" : "Occasion"}</span>
      ${img}
      <div class="card-body">
        <div class="card-marque">${v.marque}</div>
        <div class="card-titre">${v.modele}${v.version ? " <span style='font-size:16px;color:var(--silver)'>" + v.version + "</span>" : ""}</div>
        <div class="card-specs">
          <span class="spec-tag">${v.annee}</span>
          <span class="spec-tag">${energieLabel[v.energie] || v.energie}</span>
          ${v.etat !== "neuf" ? `<span class="spec-tag">${fmt.km(v.kilometrage)}</span>` : ""}
          <span class="spec-tag">${v.boite === "automatique" ? "Auto" : "Manu"}</span>
        </div>
        <div class="card-footer">
          <div>
            ${prixBarre}
            <div class="card-prix">${fmt.prix(v.prix)}</div>
          </div>
          <div class="card-agence">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:middle;margin-right:3px">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
            </svg>
            ${v.agence || ""}
          </div>
        </div>
      </div>
    </article>`;
}

/* ── Pagination ──────────────────────────────────────────── */
function renderPagination(totalPages) {
  const el = document.getElementById("pagination");
  if (totalPages <= 1) { el.innerHTML = ""; return; }

  let html = "";

  if (state.page > 1)
    html += `<button class="page-btn" data-p="${state.page - 1}">‹</button>`;

  for (let p = Math.max(1, state.page - 2); p <= Math.min(totalPages, state.page + 2); p++) {
    html += `<button class="page-btn ${p === state.page ? "active" : ""}" data-p="${p}">${p}</button>`;
  }

  if (state.page < totalPages)
    html += `<button class="page-btn" data-p="${state.page + 1}">›</button>`;

  el.innerHTML = html;
  el.querySelectorAll(".page-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      state.page = parseInt(btn.dataset.p);
      loadVehicules();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });
}

/* ── Modal détail ────────────────────────────────────────── */
async function openModal(uuid) {
  const modal   = document.getElementById("vehicle-modal");
  const content = document.getElementById("modal-content");
  content.innerHTML = `<div class="grid-loader" style="padding:60px"><div class="loader-spinner"></div></div>`;
  modal.hidden = false;
  document.body.style.overflow = "hidden";

  try {
    const v = await Api.vehicules.get(uuid);

    const imgHtml = v.photo
      ? `<img src="${v.photo}" alt="${v.marque} ${v.modele}" style="width:100%;height:100%;object-fit:cover"/>`
      : `<div style="padding:40px;color:#333;text-align:center">Pas de photo disponible</div>`;

    const specs = [
      { label: "Année",       val: v.annee },
      { label: "Énergie",     val: energieLabel[v.energie] || v.energie },
      { label: "Kilométrage", val: v.etat !== "neuf" ? fmt.km(v.kilometrage) : "0 km" },
      { label: "Boîte",       val: v.boite === "automatique" ? "Automatique" : "Manuelle" },
      { label: "Puissance",   val: v.puissance_cv ? v.puissance_cv + " ch" : "—" },
      { label: "CO₂",         val: v.co2 ? v.co2 + " g/km" : "—" },
      { label: "Couleur",     val: v.couleur_ext || "—" },
      { label: "Agence",      val: v.agence || "—" },
    ];

    const specsHtml = specs.map(s => `
      <div class="modal-spec">
        <div class="modal-spec-label">${s.label}</div>
        <div class="modal-spec-val">${s.val}</div>
      </div>`).join("");

    const prixBarre = v.prix_barre
      ? `<div style="font-size:14px;color:#555;text-decoration:line-through;margin-bottom:4px">${fmt.prix(v.prix_barre)}</div>` : "";

    const isAuth = Api.auth.isLoggedIn();
    const actionsHtml = isAuth
      ? `<a href="#" class="btn-primary btn-rdv" onclick="openRdvForm('${v.uuid}'); return false;">
           Prendre rendez-vous
         </a>
         <a href="#" class="btn-secondary" onclick="openMessage('${v.uuid}'); return false;" style="justify-content:center">
           Poser une question
         </a>`
      : `<a href="/login.html?redirect=/vehicules.html" class="btn-primary btn-rdv">
           Se connecter pour réserver
         </a>`;

    const descHtml = v.description
      ? `<div style="margin-top:20px;padding-top:16px;border-top:1px solid var(--border)">
           <p style="font-family:var(--font-body);font-size:14px;font-weight:300;color:var(--silver);line-height:1.7">${v.description}</p>
         </div>` : "";

    content.innerHTML = `
      <div class="modal-vehicle-grid">
        <div class="modal-gallery">${imgHtml}</div>
        <div class="modal-info">
          <div class="modal-marque">${v.marque}</div>
          <div class="modal-titre">${v.modele}</div>
          <div class="modal-version">${v.version || ""}</div>
          ${prixBarre}
          <div class="modal-prix">${fmt.prix(v.prix)}</div>
          <div class="modal-specs-grid">${specsHtml}</div>
          <div class="modal-actions">${actionsHtml}</div>
          ${descHtml}
        </div>
      </div>`;
  } catch (err) {
    content.innerHTML = `<div class="empty-state"><p style="color:var(--red)">Impossible de charger ce véhicule.</p></div>`;
  }
}

function closeModal() {
  document.getElementById("vehicle-modal").hidden = true;
  document.body.style.overflow = "";
}

async function openRdvForm(vehiculeUuid) {
  // Ouvre une fenêtre simple de prise de RDV (à étendre selon UX)
  const agences = await Api.agences.list();
  const agenceOptions = agences.map(a => `<option value="${a.id}">${a.ville}</option>`).join("");

  const content = document.getElementById("modal-content");
  content.innerHTML = `
    <div style="padding:40px">
      <h2 style="font-family:var(--font-head);font-size:32px;letter-spacing:2px;color:var(--white);margin-bottom:24px">
        PRENDRE <span style="color:var(--red)">RENDEZ-VOUS</span>
      </h2>
      <form id="rdv-form" style="display:flex;flex-direction:column;gap:16px">
        <label style="font-family:var(--font-sub);font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--silver)">
          Agence
          <select name="agence_id" class="filter-input" style="margin-top:6px" required>${agenceOptions}</select>
        </label>
        <label style="font-family:var(--font-sub);font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--silver)">
          Type de rendez-vous
          <select name="type_rdv" class="filter-input" style="margin-top:6px">
            <option value="essai">Essai routier</option>
            <option value="livraison">Livraison</option>
            <option value="expertise">Expertise</option>
          </select>
        </label>
        <label style="font-family:var(--font-sub);font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--silver)">
          Date & heure
          <input type="datetime-local" name="date_heure" class="filter-input" style="margin-top:6px" required/>
        </label>
        <label style="font-family:var(--font-sub);font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--silver)">
          Notes (optionnel)
          <textarea name="notes" class="filter-input" rows="3" style="margin-top:6px;resize:vertical"></textarea>
        </label>
        <button type="submit" class="btn-primary" style="justify-content:center">Confirmer le rendez-vous</button>
        <div id="rdv-msg"></div>
      </form>
    </div>`;

  document.getElementById("rdv-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const payload = {
      agence_id:    parseInt(fd.get("agence_id")),
      type_rdv:     fd.get("type_rdv"),
      date_heure:   fd.get("date_heure"),
      notes:        fd.get("notes"),
      vehicule_uuid: vehiculeUuid,
    };
    try {
      await Api.rdv.create(payload);
      document.getElementById("rdv-msg").innerHTML =
        `<p style="color:#4caf50;font-family:var(--font-sub);margin-top:8px">✓ Rendez-vous enregistré !</p>`;
      setTimeout(closeModal, 2000);
    } catch (err) {
      document.getElementById("rdv-msg").innerHTML =
        `<p style="color:var(--red);font-family:var(--font-sub);margin-top:8px">Erreur : ${err.message}</p>`;
    }
  });
}

/* ── Événements ──────────────────────────────────────────── */
function bindEvents() {

  // Tabs neuf / occasion
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.etat = btn.dataset.etat;
      state.page = 1;
      loadVehicules();
    });
  });

  // Tri
  document.getElementById("sort-select").addEventListener("change", (e) => {
    state.sort = e.target.value;
    state.page = 1;
    loadVehicules();
  });

  // Range prix
  const prixRange = document.getElementById("filter-prix-max");
  prixRange.addEventListener("input", () => {
    document.getElementById("prix-max-val").textContent =
      fmt.prix(parseInt(prixRange.value));
  });

  // Range km
  const kmRange = document.getElementById("filter-km-max");
  kmRange.addEventListener("input", () => {
    document.getElementById("km-max-val").textContent =
      fmt.km(parseInt(kmRange.value));
  });

  // Chips énergie
  document.querySelectorAll("#filter-energie .chip").forEach(chip => {
    chip.addEventListener("click", () => {
      document.querySelectorAll("#filter-energie .chip").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
    });
  });

  // Appliquer les filtres
  document.getElementById("btn-apply-filters").addEventListener("click", () => {
    const activeChip = document.querySelector("#filter-energie .chip.active");
    state.filters.q         = document.getElementById("filter-search").value.trim();
    state.filters.energie   = activeChip ? activeChip.dataset.val : "";
    state.filters.agence_id = document.getElementById("filter-agence").value;
    state.filters.annee_min = document.getElementById("filter-annee").value;
    state.filters.prix_max  = parseInt(document.getElementById("filter-prix-max").value) || null;
    state.filters.km_max    = parseInt(document.getElementById("filter-km-max").value) || null;
    state.page = 1;
    loadVehicules();
  });

  // Reset filtres
  document.getElementById("btn-reset-filters").addEventListener("click", () => {
    state.filters = { q:"", energie:"", agence_id:"", annee_min:"", prix_max:null, km_max:null };
    document.getElementById("filter-search").value = "";
    document.getElementById("filter-agence").value = "";
    document.getElementById("filter-annee").value  = "";
    document.getElementById("filter-prix-max").value = 100000;
    document.getElementById("filter-km-max").value  = 300000;
    document.getElementById("prix-max-val").textContent = "100 000 €";
    document.getElementById("km-max-val").textContent   = "300 000 km";
    document.querySelectorAll("#filter-energie .chip").forEach((c, i) => {
      c.classList.toggle("active", i === 0);
    });
    state.page = 1;
    loadVehicules();
  });

  // Fermer modal
  document.getElementById("modal-close").addEventListener("click", closeModal);
  document.getElementById("vehicle-modal").addEventListener("click", (e) => {
    if (e.target === e.currentTarget) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
}
