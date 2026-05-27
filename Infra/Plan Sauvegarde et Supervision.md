# Plan de Sauvegarde et de Supervision

## 1. Stratégie de Sauvegarde

### 1.1 La Règle du 3-2-1
Nous appliquons la méthode standard de l'industrie :
* **3 copies des données** : La donnée de production + 2 sauvegardes.
* **2 supports différents** : Stockage bloc (Disques VM) et stockage objet (Cloud Storage).
* **1 copie hors-site** : Stockage dans une région Cloud différente de la production (Géo-réplication).

### 1.2 Matrice des Sauvegardes
| Type de Ressource | Fréquence | Rétention 
| :--- | :--- | :---
| **Bases de Données (SQL)** | Toutes les heures | 35 jours 
| **Serveurs Web / Apps** | Quotidien (2h00) | 3 mois 
| **Serveurs de Fichiers** | Quotidien (Incremental) | 1 an
| **Configs pfSense / VPN** | Hebdomadaire | Indéfini 
## 2. Plan de Supervision 

### 2.1 Architecture de Supervision

* **Collecteur :** Prometheus / Zabbix.
* **Visualisation :** Grafana (Dashboards temps réel).
* **Alerting :** Notifications via Webhook (Discord/Slack/Teams) et Email.

## 3. Plan de Reprise d'Activité (PRA)

En cas de panne majeure du Hub central :

1.  **RPO (Recovery Point Objective) :** Maximum 1 heure de perte de données.
2.  **RTO (Recovery Time Objective) :** Remise en service sous 4 heures.
3.  **Procédure :** Redéploiement automatisé via Infrastructure as Code (Terraform/Ansible) et restauration des derniers snapshots immuables.

## 4. Maintenance Préventive
* **Mise à jour (Patching) :** Déploiement des correctifs de sécurité pfSense et OS tous les mois (fenêtre de maintenance à 22h00).
* **Test de Restauration :** Un test de restauration complet est effectué chaque trimestre pour valider l'intégrité des sauvegardes.