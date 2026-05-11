# Budget Infrastructure — INFRA

## SITE PRINCIPAL — Aix-en-Provence

### Serveurs

| # | Désignation | Caractéristiques | Qté | Prix unitaire | Total |
|---|---|---|:---:|---:|---:|
| 1 | Serveur SRV1 — Hyperviseur | Dell PowerEdge R350 · RAM 64Go ECC · CPU Xeon E-2300 · 2×480Go SSD + 2×4To HDD · Héberge : pfSense VM, VM-AD, VM-BDD | 1 | 2 800 € | 2 800 € |
| 2 | Serveur SRV2 — Fichiers & Backup | Dell PowerEdge R350 · RAM 32Go ECC · CPU Xeon E-2300 · 4×4To HDD RAID5 · Fichiers + Sauvegardes | 1 | 2 200 € | 2 200 € |

**Sous-total : 5 000 €**

---

### Réseau & Sécurité — Siège

| # | Désignation | Caractéristiques | Qté | Prix unitaire | Total |
|---|---|---|:---:|---:|---:|
| 3 | Switch manageable 24 ports | Cisco CBS250-24P-4G · PoE+ · 4×SFP · VLAN LAN / DMZ Web / DMZ BDD | 1 | 650 € | 650 € |
| 4 | Câbles RJ45 Cat6A (lot siège) | Câbles patch + tirage · longueurs variées | 1 | 150 € | 150 € |
| 5 | Onduleur (UPS) rack | APC Smart-UPS 1500VA · autonomie ~15min · SNMP | 2 | 480 € | 960 € |

**Sous-total : 1 760 €**

### Postes de travail — Siège (30 postes)

| # | Désignation | Caractéristiques | Qté | Prix unitaire | Total |
|---|---|---|:---:|---:|---:|
| 6 | PC fixe / Tour | Intel Core i5-13xxx · 16Go RAM · SSD 512Go · Windows 11 Pro · Écran 24" inclus | 25 | 950 € | 23 750 € |
| 7 | PC portable | Intel Core i5 · 16Go RAM · SSD 512Go · Windows 11 Pro · 14" ou 15" | 5 | 1 100 € | 5 500 € |

**Sous-total : 29 250 €**

---

### Périphériques — Siège

| # | Désignation | Caractéristiques | Qté | Prix unitaire | Total |
|---|---|---|:---:|---:|---:|
| 8 | Imprimante multifonction réseau | HP LaserJet Pro MFP · Impression/Scan/Copie · Recto-verso · IP fixe 192.168.1.30 | 1 | 420 € | 420 € |

**Sous-total : 420 €**

---

### Logiciels & Licences — Siège

| # | Désignation | Caractéristiques | Qté | Prix unitaire | Total |
|---|---|---|:---:|---:|---:|
| 9 | Windows Server 2022 Standard | Licence OEM · AD/DC, DNS, DHCP, NFS · SRV1 + SRV2 | 2 | 750 € | 1 500 € |
| 10 | Microsoft 365 Business Standard | Teams, Word, Excel, Outlook · OneDrive 1To · **annuel** | 30 | 150 €/an | 4 500 €/an |
| 11 | Antivirus / EDR — Siège | ESET Endpoint Security · licence 3 ans | 30 | 45 € | 1 350 € |
| 12 | Logiciel de sauvegarde | Veeam Backup Essentials · VMs + fichiers · **annuel** | 1 | 600 €/an | 600 €/an |

**Sous-total : 8 850 €** *(dont 5 100 €/an récurrents)*

---

### Installation & Prestations — Siège

| # | Désignation | Caractéristiques | Qté | Prix unitaire | Total |
|---|---|---|:---:|---:|---:|
| 13 | Installation & configuration serveurs | Montage, OS, hyperviseur Proxmox, AD, DNS, DHCP, mise en production | 1 | 1 200 € | 1 200 € |
| 14 | Configuration pfSense + 2 DMZ | Pare-feu, règles, DMZ Web, DMZ BDD, règles inter-DMZ, documentation | 1 | 1 000 € | 1 000 € |
| 15 | Configuration 12 tunnels VPN IPsec | IKEv2 AES-256 · 12 tunnels site-to-site · tests + doc | 1 | 1 500 € | 1 500 € |
| 16 | Câblage réseau siège (main d'œuvre) | Tirage câbles, poses prises, baie de brassage, étiquetage | 1 | 600 € | 600 € |
| 17 | Formation utilisateurs siège | Demi-journée · 30 utilisateurs · prise en main M365 | 1 | 400 € | 400 € |
| 18 | Maintenance annuelle siège (contrat) | Support prioritaire, MAJ, supervision, astreinte · **annuel** | 1 | 2 400 €/an | 2 400 €/an |

**Sous-total : 4 700 €** *(+ 2 400 €/an)*

---
---

## SITES DISTANTS — 12 Agences

### Réseau & Sécurité — Par agence (×12)

| # | Désignation | Caractéristiques | Qté/site | Prix unitaire | Total/site | Total ×12 |
|---|---|---|:---:|---:|---:|---:|
| 19 | Routeur/Pare-feu pfSense | Appliance dédiée Protectli VP2420 · 4×Intel i226 · 8Go RAM · 64Go SSD | 1 | 450 € | 450 € | 5 400 € |
| 20 | Switch 8 ports | Cisco CBS110-8PP · PoE · non manageable | 1 | 120 € | 120 € | 1 440 € |
| 21 | Câbles RJ45 Cat6 (lot agence) | Câbles patch · longueurs variées | 1 | 50 € | 50 € | 600 € |
| 22 | Onduleur (UPS) bureau | APC Back-UPS 700VA · protection équipements réseau | 1 | 120 € | 120 € | 1 440 € |

**Sous-total agences réseau : 8 880 €**

---

### Postes de travail — Par agence (×12)

| # | Désignation | Caractéristiques | Qté/site | Prix unitaire | Total/site | Total ×12 |
|---|---|---|:---:|---:|---:|---:|
| 23 | PC fixe / Tour agence | Intel Core i5 · 16Go RAM · SSD 512Go · Windows 11 Pro · Écran 22" inclus | 5 | 900 € | 4 500 € | 54 000 € |

**Sous-total agences postes : 54 000 €**

---

### Périphériques — Par agence (×12)

| # | Désignation | Caractéristiques | Qté/site | Prix unitaire | Total/site | Total ×12 |
|---|---|---|:---:|---:|---:|---:|
| 24 | Imprimante réseau agence | HP LaserJet Pro · Impression/Scan · IP fixe 192.168.X.30 | 1 | 320 € | 320 € | 3 840 € |

**Sous-total agences périphériques : 3 840 €**

---

### Logiciels & Licences — Agences

| # | Désignation | Caractéristiques | Qté | Prix unitaire | Total |
|---|---|---|:---:|---:|---:|
| 25 | Microsoft 365 Business Standard | Teams, Word, Excel, Outlook · **annuel** · 5 users × 12 sites | 60 | 150 €/an | 9 000 €/an |
| 26 | Antivirus / EDR — Agences | ESET Endpoint Security · licence 3 ans · 5 postes × 12 sites | 60 | 45 € | 2 700 € |

**Sous-total agences licences : 11 700 €** *(dont 9 000 €/an récurrents)*

---

### Installation & Prestations — Agences

| # | Désignation | Caractéristiques | Qté | Prix unitaire | Total |
|---|---|---|:---:|---:|---:|
| 27 | Installation on-site par agence | Config pfSense, switch, postes, VPN, imprimante · déplacement inclus | 12 | 600 € | 7 200 € |
| 28 | Formation utilisateurs agences | Demi-journée par agence · 5 utilisateurs | 12 | 200 € | 2 400 € |
| 29 | Maintenance annuelle agences | Support à distance · MAJ pfSense · supervision VPN · **annuel** | 12 | 600 €/an | 7 200 €/an |

**Sous-total agences prestations : 9 600 €** *(+ 7 200 €/an)*

---
---

## Récapitulatif Global

### Budget initial (investissement unique)

| Catégorie | Site | Montant HT | % |
|---|---|---:|:---:|
| Serveurs | Siège | 5 000 € | 3 % |
| Réseau & Sécurité | Siège | 1 760 € | 1 % |
| Postes de travail | Siège (30 postes) | 29 250 € | 18 % |
| Périphériques | Siège | 420 € | — |
| Logiciels & Licences | Siège | 3 450 € | 2 % |
| Installation & Prestations | Siège | 4 700 € | 3 % |
| Réseau & Sécurité | 12 Agences | 8 880 € | 5 % |
| Postes de travail | 12 Agences (60 postes) | 54 000 € | 33 % |
| Périphériques | 12 Agences | 3 840 € | 2 % |
| Logiciels & Licences | 12 Agences | 2 700 € | 2 % |
| Installation & Prestations | 12 Agences | 9 600 € | 6 % |
| **TOTAL HT** | | **123 600 €** | **100 %** |
| TVA 20% | | 24 720 € | — |
| **TOTAL TTC** | | **148 320 €** | — |

---

### Coûts récurrents annuels

| Poste | Périmètre | Coût annuel |
|---|---|---:|
| Microsoft 365 (30 users) | Siège | 4 500 € |
| Microsoft 365 (60 users) | 12 Agences | 9 000 € |
| Logiciel de sauvegarde | Siège | 600 € |
| Contrat maintenance | Siège | 2 400 € |
| Contrat maintenance | 12 Agences | 7 200 € |
| Certificats SSL + domaine | Siège | ~115 € |
| **Total annuel** | | **~23 815 €** |

---

## Synthèse par périmètre

| Périmètre | Investissement HT | Coût annuel |
|---|---:|---:|
| 🏢 Siège Aix-en-Provence | 44 580 € | 7 615 € |
| 🏪 12 Agences (total) | 79 020 € | 16 200 € |
| **TOTAL** | **123 600 €** | **23 815 €** |
