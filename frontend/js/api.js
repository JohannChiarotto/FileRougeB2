/**
 * api.js — Client HTTP centralisé pour l'API Darri-Bolide
 * Gère l'authentification JWT, les erreurs et la pagination.
 */

const API_BASE = "/api";

const Api = (() => {

  // ── Tokens ─────────────────────────────────────────────────
  const getToken   = () => localStorage.getItem("access_token");
  const setToken   = (t) => localStorage.setItem("access_token", t);
  const clearToken = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  };

  // ── Fetch wrapper ───────────────────────────────────────────
  async function request(method, path, body = null, auth = false) {
    const headers = { "Content-Type": "application/json" };
    if (auth) {
      const token = getToken();
      if (token) headers["Authorization"] = `Bearer ${token}`;
    }

    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(API_BASE + path, opts);

    // Token expiré → essayer le refresh
    if (res.status === 401 && auth) {
      const refreshed = await tryRefresh();
      if (refreshed) return request(method, path, body, auth);
      clearToken();
      window.location.href = "/login.html";
      return;
    }

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Erreur HTTP ${res.status}`);
    }

    return res.json();
  }

  async function tryRefresh() {
    const rt = localStorage.getItem("refresh_token");
    if (!rt) return false;
    try {
      const res = await fetch(API_BASE + "/auth/refresh", {
        method: "POST",
        headers: {
          "Content-Type":  "application/json",
          "Authorization": `Bearer ${rt}`,
        },
      });
      if (!res.ok) return false;
      const data = await res.json();
      setToken(data.access_token);
      return true;
    } catch {
      return false;
    }
  }

  // ── Auth ────────────────────────────────────────────────────
  const auth = {
    async login(email, password) {
      const data = await request("POST", "/auth/login", { email, password });
      localStorage.setItem("access_token",  data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      return data.user;
    },

    async register(payload) {
      return request("POST", "/auth/register", payload);
    },

    async me() {
      return request("GET", "/auth/me", null, true);
    },

    logout() {
      clearToken();
      window.location.href = "/login.html";
    },

    currentUser() {
      const u = localStorage.getItem("user");
      return u ? JSON.parse(u) : null;
    },

    isLoggedIn() {
      return !!getToken();
    },
  };

  // ── Véhicules ───────────────────────────────────────────────
  const vehicules = {
    list(params = {}) {
      const qs = new URLSearchParams(
        Object.fromEntries(Object.entries(params).filter(([, v]) => v !== "" && v != null))
      ).toString();
      return request("GET", `/vehicules/?${qs}`);
    },

    get(uuid) {
      return request("GET", `/vehicules/${uuid}`);
    },

    create(data) {
      return request("POST", "/vehicules/", data, true);
    },

    update(uuid, data) {
      return request("PUT", `/vehicules/${uuid}`, data, true);
    },

    remove(uuid) {
      return request("DELETE", `/vehicules/${uuid}`, null, true);
    },

    uploadPhoto(uuid, file) {
      const fd = new FormData();
      fd.append("file", file);
      return fetch(`${API_BASE}/vehicules/${uuid}/photos`, {
        method:  "POST",
        headers: { "Authorization": `Bearer ${getToken()}` },
        body:    fd,
      }).then(r => r.json());
    },

    marques() {
      return request("GET", "/vehicules/marques/list");
    },

    stats() {
      return request("GET", "/vehicules/stats/summary", null, true);
    },
  };

  // ── Agences ─────────────────────────────────────────────────
  const agences = {
    list() {
      return request("GET", "/agences/");
    },
    get(id) {
      return request("GET", `/agences/${id}`);
    },
  };

  // ── Messages / Conversations ─────────────────────────────────
  const messages = {
    listConversations() {
      return request("GET", "/messages/conversations", null, true);
    },

    getConversation(id) {
      return request("GET", `/messages/conversations/${id}`, null, true);
    },

    createConversation(payload) {
      return request("POST", "/messages/conversations", payload, true);
    },

    sendMessage(convId, contenu) {
      return request("POST", `/messages/conversations/${convId}`, { contenu }, true);
    },

    updateStatut(convId, statut) {
      return request("PATCH", `/messages/conversations/${convId}/statut`, { statut }, true);
    },
  };

  // ── RDV ──────────────────────────────────────────────────────
  const rdv = {
    list() {
      return request("GET", "/rdv/", null, true);
    },

    create(payload) {
      return request("POST", "/rdv/", payload, true);
    },

    updateStatut(id, statut) {
      return request("PATCH", `/rdv/${id}/statut`, { statut }, true);
    },
  };

  // ── Estimation véhicule ──────────────────────────────────────
  const estimation = {
    createRequest(data) {
      return request("POST", "/vehicules/estimate", data);
    },
    listRequests() {
      return request("GET", "/vehicules/estimate/requests", null, true);
    },
    updateRequest(id, payload) {
      return request("PATCH", `/vehicules/estimate/requests/${id}`, payload, true);
    },
  };

  // ── Helpers publiques ────────────────────────────────────────
  const helpers = {
    updateNavAuth() {
      const user = auth.currentUser();
      const navAuth = document.getElementById("nav-auth");
      if (!navAuth) return;
      if (user) {
        const adminLink = (user.role === "admin" || user.role === "vendeur")
          ? `<a href="/admin-estimations.html" class="btn-ghost-sm">Demandes estimation</a>`
          : "";
        navAuth.innerHTML = `
          <span style="font-family:var(--font-sub);font-size:12px;letter-spacing:2px;color:var(--silver)">
            ${user.prenom}
          </span>
          ${adminLink}
          <button onclick="Api.auth.logout()" class="btn-ghost-sm">Déconnexion</button>`;
      }
    }
  };

  return { auth, vehicules, agences, messages, rdv, estimation, helpers };
})();
