# Politique de Sécurité du Système d'Information

## 1. Introduction et Périmètre
### 1.1 Objet du document
- Ce document définit la Politique de Sécurité du Système d'Information applicable à l'ensemble de l'infrastructure IT du projet. Il couvre l'environnement Windows Server, l'infrastructure réseau multi-sites (siège + agences), les services d'annuaire Active Directory et les mécanismes de protection périmétrique.

### 1.2 Périmètre d'application
- La présente politique s'applique à :
    - L'ensemble des serveurs Windows
    - L'infrastructure réseau : routeurs, commutateurs, pare-feux, points d'accès Wi-Fi
    - Les liaisons VPN/IPSec inter-sites reliant le siège aux agences distantes
    - Les services réseau : DNS, DHCP, NAT, proxy
    - Les postes de travail et terminaux utilisateurs membres du domaine
    - Les comptes utilisateurs et administrateurs gérés dans Active Directory

### 1.3 Objectifs de sécurité
Disponibilité · Intégrité · Confidentialité · Traçabilité

## 2. Sécurité Active Directory
### 2.1 Stratégies de groupe
#### 2.2.1 GPO de sécurité
- Politique de mots de passe : longueur minimale 12 caractères, complexité activée, historique 24 mots de passe, durée maximale 90 jours
- Verrouillage de compte : 5 tentatives échouées, déverrouillage après 30 minutes
- Restriction des ports USB sur les postes sensibles
- Activation du pare-feu Windows sur tous les postes
- Désactivation de PowerShell v2, activation du logging PowerShell
## 3. Sécurité des Services Réseau
### 3.1 DNS
- Serveurs DNS internes séparés des DNS publics
- Restriction des transferts de zone aux seuls serveurs DNS secondaires autorisés
- Journalisation des requêtes DNS
- Filtrage DNS : blocage des domaines malveillants via RPZ 

### 3.2 DHCP
- Activation du filtrage MAC ou de la protection contre le DHCP Snooping
- Réservations IP pour tous les serveurs et équipements réseau
- Durées de bail : 2h pour les invités, 8h pour les postes du domaine
- Journalisation de toutes les attributions DHCP
### 3.3 NAT et accès Internet

- NAT source activé sur le pare-feu
- Liste blanche d'URL
- Blocage par défaut des catégories à risque : malware, phishing, P2P, anonymiseurs

## 4. Politique de Pare-feu et Filtrage
### 4.1 Principe général

- Tout ce qui n'est pas explicitement autorisé est interdit (Default Deny).

### 4.2 Filtrage du pare-feu
- Tout refuser , zero trut , execpté les flux métiers (DNS,HTTPS,Partage de fichiers,AD,..)

## 5. Surveillance, Journalisation

- Journaux d'authentification Windows (Event ID 4624, 4625, 4648, 4768, 4769)
- Journaux de modification Active Directory (Event ID 4720, 4722, 4728, 4732)
- Journaux pare-feu : connexions acceptées et refusées
- Journaux DHCP et DNS
- Journaux d'accès VPN (connexions, déconnexions, échecs)
- Logs des équipements réseau (syslog centralisé)

## 6. Gestion des Mises à Jour et Vulnérabilités
- Maintien d'un inventaire à jour de tous les actifs IT (matériel et logiciel)
- Scan de vulnérabilités mensuel sur l'ensemble du périmètre
- Revue et mise à jour annuelle de la politique mise en place