# Plan d'adressage IP — Ymmo

> **Client :** Ymmo — Groupe immobilier
> **Siège :** Aix-en-Provence
> **Architecture :** 1 siège + 12 agences nationales
> **Standard :** IPv4 privé RFC 1918 | Segmentation VLAN | Tunnels VPN/IPSec site-à-site

---

## Logique d'adressage global

| Plage | Périmètre |
|---|---|
| `10.0.x.x` | Siège social — Aix-en-Provence |
| `10.1.x.x` → `10.12.x.x` | Agences 01 à 12 |
| `172.16.x.x` | Backbone VPN/IPSec inter-sites |

---

## Siège — Aix-en-Provence

### Vue d'ensemble des sous-réseaux

| VLAN | Nom | Réseau | Masque | Hôtes dispo | Usage |
|---|---|---|---|---|---|
| 10 | LAN | `10.0.1.0/24` | `255.255.255.0` | 254 | ~30 postes utilisateurs |
| 20 | SRV | `10.0.2.0/24` | `255.255.255.0` | 254 | Serveurs internes |
| 30 | PRINT | `10.0.3.0/28` | `255.255.255.240` | 14 | Imprimante siège |
| 40 | DMZ | `10.0.4.0/24` | `255.255.255.0` | 254 | Serveur web (exposé) |
| 50 | MGMT | `10.0.5.0/28` | `255.255.255.240` | 14 | Équipements réseau / admin |

---

### VLAN 10 — Postes utilisateurs (`10.0.1.0/24`)

| Paramètre | Valeur |
|---|---|
| Réseau | `10.0.1.0` |
| Masque | `255.255.255.0` |
| Passerelle | `10.0.1.254` |
| Plage DHCP | `10.0.1.10` → `10.0.1.200` |
| Réservé fixe | `10.0.1.201` → `10.0.1.253` |

Répartition des postes par pôle Ymmo :

| Pôle | Plage recommandée |
|---|---|
| Direction | `10.0.1.10` → `10.0.1.19` |
| Commercial | `10.0.1.20` → `10.0.1.39` |
| Communication & Marketing | `10.0.1.40` → `10.0.1.59` |
| Administratif – RH – Juridique | `10.0.1.60` → `10.0.1.79` |
| IT et Support | `10.0.1.80` → `10.0.1.99` |

---

### VLAN 20 — Serveurs (`10.0.2.0/24`)

| Serveur | Adresse IP fixe | Rôle |
|---|---|---|
| Contrôleur de domaine (AD) | `10.0.2.1` | Active Directory, DNS, DHCP, GPO |
| Serveur de fichiers | `10.0.2.2` | Partages réseau par pôle, home drives |
| Serveur de sauvegardes | `10.0.2.3` | Backup journalier full/incrémental |
| Serveur base de données | `10.0.2.4` | SGBD Ymmo (biens, clients, transactions) |
| Passerelle VLAN SRV | `10.0.2.254` | Gateway serveurs |

---

### VLAN 30 — Impression (`10.0.3.0/28`)

| Équipement | Adresse IP fixe | Notes |
|---|---|---|
| Imprimante siège | `10.0.3.2` | IP fixe — réseau isolé |
| Passerelle | `10.0.3.1` | Gateway impression |

---

### VLAN 40 — DMZ / Hébergement web (`10.0.4.0/24`)

| Serveur | Adresse IP fixe | Rôle |
|---|---|---|
| Serveur web Ymmo | `10.0.4.10` | Plateforme web achat/vente immobilier |
| Passerelle DMZ | `10.0.4.254` | Gateway DMZ |

> ⚠️ La DMZ est strictement isolée du LAN et des serveurs internes par le pare-feu. Aucun flux entrant depuis la DMZ vers `10.0.1.x` ou `10.0.2.x` n'est autorisé.

---

### VLAN 50 — Gestion réseau (`10.0.5.0/28`)

| Équipement | Adresse IP fixe | Rôle |
|---|---|---|
| Pare-feu | `10.0.5.1` | Filtrage WAN / LAN / DMZ / VPN |
| Routeur principal | `10.0.5.2` | Routage inter-VLAN + accès WAN |
| Switch cœur | `10.0.5.3` | Administration réseau interne |

> Accès restreint aux administrateurs IT uniquement (pôle IT et Support).

---

## Agences (×12)

### Schéma type — Agence `[N]`

Chaque agence applique le même modèle. `[N]` = numéro de l'agence (1 à 12).

| Segment | Réseau | Masque | Passerelle | Usage |
|---|---|---|---|---|
| Postes | `10.[N].1.0/24` | `255.255.255.0` | `10.[N].1.254` | ~5 postes commerciaux |
| Impression | `10.[N].2.0/28` | `255.255.255.240` | `10.[N].2.1` | 1 imprimante fixe : `10.[N].2.2` |
| Tunnel VPN | `172.16.[N].0/30` | `255.255.255.252` | — | Lien IPSec chiffré vers le siège |

Plage DHCP postes agence : `10.[N].1.10` → `10.[N].1.20`

---

### Tableau récapitulatif des 12 agences

| Agence | Réseau postes | Passerelle | DHCP postes | Imprimante | Tunnel VPN |
|---|---|---|---|---|---|
| Agence 01 | `10.1.1.0/24` | `10.1.1.254` | `.10` → `.20` | `10.1.2.2` | `172.16.1.0/30` |
| Agence 02 | `10.2.1.0/24` | `10.2.1.254` | `.10` → `.20` | `10.2.2.2` | `172.16.2.0/30` |
| Agence 03 | `10.3.1.0/24` | `10.3.1.254` | `.10` → `.20` | `10.3.2.2` | `172.16.3.0/30` |
| Agence 04 | `10.4.1.0/24` | `10.4.1.254` | `.10` → `.20` | `10.4.2.2` | `172.16.4.0/30` |
| Agence 05 | `10.5.1.0/24` | `10.5.1.254` | `.10` → `.20` | `10.5.2.2` | `172.16.5.0/30` |
| Agence 06 | `10.6.1.0/24` | `10.6.1.254` | `.10` → `.20` | `10.6.2.2` | `172.16.6.0/30` |
| Agence 07 | `10.7.1.0/24` | `10.7.1.254` | `.10` → `.20` | `10.7.2.2` | `172.16.7.0/30` |
| Agence 08 | `10.8.1.0/24` | `10.8.1.254` | `.10` → `.20` | `10.8.2.2` | `172.16.8.0/30` |
| Agence 09 | `10.9.1.0/24` | `10.9.1.254` | `.10` → `.20` | `10.9.2.2` | `172.16.9.0/30` |
| Agence 10 | `10.10.1.0/24` | `10.10.1.254` | `.10` → `.20` | `10.10.2.2` | `172.16.10.0/30` |
| Agence 11 | `10.11.1.0/24` | `10.11.1.254` | `.10` → `.20` | `10.11.2.2` | `172.16.11.0/30` |
| Agence 12 | `10.12.1.0/24` | `10.12.1.254` | `.10` → `.20` | `10.12.2.2` | `172.16.12.0/30` |

---

## VPN / IPSec — Backbone inter-sites

| Paramètre | Valeur |
|---|---|
| Plage dédiée | `172.16.0.0/16` |
| Type | IPSec site-à-site |
| Chiffrement | AES-256 |
| Authentification | Certificats X.509 |
| Terminaison siège | Pare-feu `10.0.5.1` |
| Nombre de tunnels | 12 (un par agence) |

Chaque tunnel utilise un `/30` dédié (2 adresses utiles : une extrémité siège, une extrémité agence). Cela garantit l'isolation complète entre tunnels.

| Tunnel | Extrémité siège | Extrémité agence |
|---|---|---|
| Agence 01 | `172.16.1.1` | `172.16.1.2` |
| Agence 02 | `172.16.2.1` | `172.16.2.2` |
| … | … | … |
| Agence 12 | `172.16.12.1` | `172.16.12.2` |

---

## Conventions d'attribution

| Suffixe | Rôle réservé |
|---|---|
| `.1` | Première adresse utile / routeur local |
| `.2` → `.9` | Équipements fixes (switch, AP, imprimante) |
| `.10` → `.200` | Plage DHCP postes utilisateurs |
| `.201` → `.253` | Réservé — extensions futures |
| `.254` | Passerelle par défaut |
| `.255` | Broadcast |

---

## Politique de sécurité réseau (synthèse)

| Règle | Détail |
|---|---|
| Pare-feu | Filtrage stateful entre chaque VLAN et la DMZ |
| DMZ | Aucun flux entrant vers LAN ou SRV depuis la DMZ |
| VPN | Tout le trafic agence ↔ siège est chiffré AES-256 |
| MGMT | Accès restreint au VLAN 50, administrateurs IT uniquement |
| AD/DNS/DHCP | Centralisé sur `10.0.2.1`, accessible depuis tous les VLANs internes |
| GPO | Stratégies de groupe définies par pôle via Active Directory |
| Sauvegardes | Backup journalier vers `10.0.2.3`, rétention 30 jours |

---

## Matrice des droits — correspondance réseau

Basée sur la matrice des droits Ymmo (dossiers partagés par pôle) :

| Pôle | VLAN | Accès serveur fichiers |
|---|---|---|
| Direction | VLAN 10 — `10.0.1.10/19` | Lecture / Écriture tous dossiers |
| Commercial | VLAN 10 — `10.0.1.20/39` | Lecture / Écriture dossier Commercial uniquement |
| Communication & Marketing | VLAN 10 — `10.0.1.40/59` | Lecture / Écriture dossier Comm. uniquement |
| Administratif – RH – Juridique | VLAN 10 — `10.0.1.60/79` | Lecture / Écriture dossier Admin uniquement |
| IT et Support | VLAN 10 — `10.0.1.80/99` | Lecture / Écriture dossier IT + accès MGMT |
| Commerciaux agences | VLAN agence `10.[N].1.x` | Accès via VPN — dossier Commercial (lecture) |