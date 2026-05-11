# Tableau d'adressage IP

## Site Principal — Aix-en-Provence

### Équipements réseau & serveurs

| Équipement | Rôle | Adresse IP | Masque | Passerelle | Attribution |
|---|---|---|---|---|---|
| pfSense (WAN) | Interface publique FAI | IP FAI | Selon FAI | IP FAI | Fixe |
| pfSense (LAN) | Routeur / Pare-feu / DHCP | 192.168.1.1 | 255.255.255.0 | — | Fixe |
| pfSense (DMZ Web) | Interface DMZ Web | 192.168.2.1 | 255.255.255.0 | — | Fixe |
| pfSense (DMZ BDD) | Interface DMZ BDD | 192.168.3.1 | 255.255.255.0 | — | Fixe |
| Switch | Switch | 192.168.1.2 | 255.255.255.0 | 192.168.1.1 | Fixe |
| Windows Server | Active Directory / Fichiers / Backup | 192.168.1.10 | 255.255.255.0 | 192.168.1.1 | Fixe |
| Imprimante | Impression réseau partagée | 192.168.1.30 | 255.255.255.0 | 192.168.1.1 | Fixe |
| Postes clients (x30) | Stations de travail Windows | 192.168.1.50 – 192.168.1.250 | 255.255.255.0 | 192.168.1.1 | DHCP |

### DMZ Web — 192.168.2.0/24

| Équipement | Rôle | Adresse IP | Masque | Passerelle | Attribution |
|---|---|---|---|---|---|
| Serveur Web | Hébergement web | 192.168.2.10 | 255.255.255.0 | 192.168.2.1 | Fixe |

### DMZ BDD — 192.168.3.0/24

| Équipement | Rôle | Adresse IP | Masque | Passerelle | Attribution |
|---|---|---|---|---|---|
| Serveur BDD | Base de données (MySQL) | 192.168.3.10 | 255.255.255.0 | 192.168.3.1 | Fixe |

### Plage DHCP — LAN Aix-en-Provence

| Paramètre | Valeur |
|---|---|
| Plage d'attribution | 192.168.1.50 — 192.168.1.250 |
| Masque | 255.255.255.0 |
| Passerelle | 192.168.1.1 (pfSense) |
| DNS primaire | 192.168.1.10 (Windows Server AD) |
| DNS secondaire | 8.8.8.8 (Google) |
| Durée du bail | 24h |

---

## Sites distants — 12 agences commerciales

### Vue d'ensemble des sites

| Site | Nom | Réseau LAN | pfSense LAN | Switch | Imprimante | Postes (DHCP) |
|---|---|---|---|---|---|---|
| Site 01 | Agence 01 | 192.168.10.0/24 | 192.168.10.1 | 192.168.10.2 | 192.168.10.30 | 192.168.10.50 – .100 |
| Site 02 | Agence 02 | 192.168.11.0/24 | 192.168.11.1 | 192.168.11.2 | 192.168.11.30 | 192.168.11.50 – .100 |
| Site 03 | Agence 03 | 192.168.12.0/24 | 192.168.12.1 | 192.168.12.2 | 192.168.12.30 | 192.168.12.50 – .100 |
| Site 04 | Agence 04 | 192.168.13.0/24 | 192.168.13.1 | 192.168.13.2 | 192.168.13.30 | 192.168.13.50 – .100 |
| Site 05 | Agence 05 | 192.168.14.0/24 | 192.168.14.1 | 192.168.14.2 | 192.168.14.30 | 192.168.14.50 – .100 |
| Site 06 | Agence 06 | 192.168.15.0/24 | 192.168.15.1 | 192.168.15.2 | 192.168.15.30 | 192.168.15.50 – .100 |
| Site 07 | Agence 07 | 192.168.16.0/24 | 192.168.16.1 | 192.168.16.2 | 192.168.16.30 | 192.168.16.50 – .100 |
| Site 08 | Agence 08 | 192.168.17.0/24 | 192.168.17.1 | 192.168.17.2 | 192.168.17.30 | 192.168.17.50 – .100 |
| Site 09 | Agence 09 | 192.168.18.0/24 | 192.168.18.1 | 192.168.18.2 | 192.168.18.30 | 192.168.18.50 – .100 |
| Site 10 | Agence 10 | 192.168.19.0/24 | 192.168.19.1 | 192.168.19.2 | 192.168.19.30 | 192.168.19.50 – .100 |
| Site 11 | Agence 11 | 192.168.20.0/24 | 192.168.20.1 | 192.168.20.2 | 192.168.20.30 | 192.168.20.50 – .100 |
| Site 12 | Agence 12 | 192.168.21.0/24 | 192.168.21.1 | 192.168.21.2 | 192.168.21.30 | 192.168.21.50 – .100 |

### Détail type d'un site distant (applicable à chaque agence)

| Équipement | Rôle | Adresse IP | Masque | Passerelle | Attribution |
|---|---|---|---|---|---|
| pfSense (WAN) | Interface publique FAI | IP FAI local | Selon FAI | IP FAI | Fixe |
| pfSense (LAN) | Routeur / Pare-feu / DHCP | 192.168.X.1 | 255.255.255.0 | — | Fixe |
| Switch | Switch 8P | 192.168.X.2 | 255.255.255.0 | 192.168.X.1 | Fixe |
| Imprimante | Impression réseau partagée | 192.168.X.30 | 255.255.255.0 | 192.168.X.1 | Fixe |
| Postes commerciaux (x5) | Stations de travail Windows | 192.168.X.50 – 192.168.X.100 | 255.255.255.0 | 192.168.X.1 | DHCP |

### Plage DHCP — Sites distants (type)

| Paramètre | Valeur |
|---|---|
| Plage d'attribution | 192.168.X.50 — 192.168.X.100 |
| Masque | 255.255.255.0 |
| Passerelle | 192.168.X.1 (pfSense local) |
| DNS primaire | 192.168.1.10 (Windows Server Aix — via VPN) |
| DNS secondaire | 8.8.8.8 (Google) |
| Durée du bail | 24h |


## VPN — Tunnels IPsec Site-to-Site

| Tunnel | Site source | Site destination | Réseau source | Réseau destination | Protocole |
|---|---|---|---|---|---|
| VPN-01 | Aix-en-Provence | Agence 01 | 192.168.1.0/24 | 192.168.10.0/24 | IPsec IKEv2 |
| VPN-02 | Aix-en-Provence | Agence 02 | 192.168.1.0/24 | 192.168.11.0/24 | IPsec IKEv2 |
| VPN-03 | Aix-en-Provence | Agence 03 | 192.168.1.0/24 | 192.168.12.0/24 | IPsec IKEv2 |
| VPN-04 | Aix-en-Provence | Agence 04 | 192.168.1.0/24 | 192.168.13.0/24 | IPsec IKEv2 |
| VPN-05 | Aix-en-Provence | Agence 05 | 192.168.1.0/24 | 192.168.14.0/24 | IPsec IKEv2 |
| VPN-06 | Aix-en-Provence | Agence 06 | 192.168.1.0/24 | 192.168.15.0/24 | IPsec IKEv2 |
| VPN-07 | Aix-en-Provence | Agence 07 | 192.168.1.0/24 | 192.168.16.0/24 | IPsec IKEv2 |
| VPN-08 | Aix-en-Provence | Agence 08 | 192.168.1.0/24 | 192.168.17.0/24 | IPsec IKEv2 |
| VPN-09 | Aix-en-Provence | Agence 09 | 192.168.1.0/24 | 192.168.18.0/24 | IPsec IKEv2 |
| VPN-10 | Aix-en-Provence | Agence 10 | 192.168.1.0/24 | 192.168.19.0/24 | IPsec IKEv2 |
| VPN-11 | Aix-en-Provence | Agence 11 | 192.168.1.0/24 | 192.168.20.0/24 | IPsec IKEv2 |
| VPN-12 | Aix-en-Provence | Agence 12 | 192.168.1.0/24 | 192.168.21.0/24 | IPsec IKEv2 |

### Paramètres VPN IPsec

| Paramètre | Valeur |
|---|---|
| Protocole | IPsec IKEv2 |
| Chiffrement | AES-256 |
| Authentification | Clé pré-partagée (PSK) ou certificat |
| Hash | SHA-256 |
| DH Group | 14 (2048 bits) |
| Durée de vie SA | 28800s (Phase 1) / 3600s (Phase 2) |