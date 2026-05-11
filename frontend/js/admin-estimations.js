document.addEventListener("DOMContentLoaded", async () => {
  if (!Api.auth.isLoggedIn()) {
    window.location.href = "/login.html?redirect=/admin-estimations.html";
    return;
  }

  const user = Api.auth.currentUser();
  if (!user || (user.role !== "admin" && user.role !== "vendeur")) {
    window.location.href = "/vehicules.html";
    return;
  }

  Api.helpers.updateNavAuth();

  const listEl = document.getElementById("requests");

  async function loadRequests() {
    try {
      const items = await Api.estimation.listRequests();
      if (!items.length) {
        listEl.innerHTML = "<p>Aucune demande d'estimation pour le moment.</p>";
        return;
      }

      listEl.innerHTML = items.map((r) => `
        <article class="req-card" data-id="${r.id}">
          <div class="req-grid">
            <div><strong>ID:</strong> ${r.id}</div>
            <div><strong>Email:</strong> ${r.email}</div>
            <div><strong>Véhicule:</strong> ${r.marque} ${r.modele}</div>
            <div><strong>Année:</strong> ${r.annee}</div>
            <div><strong>Kilométrage:</strong> ${Number(r.kilometrage).toLocaleString("fr-FR")} km</div>
            <div><strong>Énergie:</strong> ${r.energie}</div>
            <div><strong>Statut:</strong> ${r.statut}</div>
            <div><strong>Créée le:</strong> ${new Date(r.created_at).toLocaleString("fr-FR")}</div>
          </div>
          <div class="req-actions">
            <select class="req-status">
              ${["en_attente", "en_cours", "traitee", "refusee"].map((s) => `
                <option value="${s}" ${r.statut === s ? "selected" : ""}>${s}</option>
              `).join("")}
            </select>
            <input class="req-comment" type="text" placeholder="Commentaire admin (optionnel)" value="${r.commentaire_admin || ""}"/>
            <button class="btn-primary req-save">Enregistrer</button>
          </div>
        </article>
      `).join("");
    } catch (err) {
      listEl.innerHTML = `<p>${err.message}</p>`;
    }
  }

  listEl.addEventListener("click", async (e) => {
    const btn = e.target.closest(".req-save");
    if (!btn) return;

    const card = btn.closest(".req-card");
    const id = Number(card.dataset.id);
    const statut = card.querySelector(".req-status").value;
    const commentaire_admin = card.querySelector(".req-comment").value.trim();

    btn.disabled = true;
    btn.textContent = "Enregistrement…";
    try {
      await Api.estimation.updateRequest(id, { statut, commentaire_admin });
      btn.textContent = "Enregistré";
      setTimeout(() => {
        btn.textContent = "Enregistrer";
        btn.disabled = false;
      }, 800);
      loadRequests();
    } catch (err) {
      btn.textContent = "Erreur";
      btn.disabled = false;
      alert(err.message);
    }
  });

  loadRequests();
});
