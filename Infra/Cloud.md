# Projet d'Infrastructure Cloud 

## 1. Solution Hub

### Schéma de principe
1. **Le Cloud (Le Hub) :** Devient le centre du réseau. Il héberge les ressources partagées (Active Directory, ERP, Fichiers).
2. **Les Agences (Les Spokes) :** Chaque agence possède son propre pfSense et se connecte uniquement au Cloud.

## 2. Détails Techniques de mise en œuvre

### A. Réseautage et Connectivité
- **VPN Gateway :** Utilisation d'une passerelle VPN managée dans le Cloud capable de supporter plusieurs tunnels simultanés.
- **Adressage IP :** Segmentation stricte pour éviter les chevauchements.
    - Hub Cloud : `10.0.0.0/16`
    - Agences : `10.x.0.0/24`.

### B. Sécurité Centralisée
- Migration de la DMZ (Serveur Web et BDD) vers un VPC/VNet Cloud.
- Mise en place d'un Pare-feu au niveau du Hub pour filtrer le trafic inter-agences et l'accès Internet.

### C. Services d'Identité
- Déploiement d'un contrôleur de domaine secondaire dans le Cloud ou synchronisation avec **Azure AD (Entra ID)** pour permettre aux utilisateurs des 12 agences de se connecter avec un compte unique.