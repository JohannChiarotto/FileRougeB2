-- Seed de démonstration Darri-Bolide
-- Idempotent: ce script peut etre relance sans dupliquer inutilement.

BEGIN;

-- Agences minimales si base vide
INSERT INTO agences (nom, adresse, ville, code_postal, telephone, email, est_siege, latitude, longitude)
SELECT *
FROM (
  VALUES
    ('Darri-Bolide Paris Centre', '10 rue de Rivoli', 'Paris', '75001', '01 23 45 67 89', 'paris@darri-bolide.fr', TRUE, 48.8566, 2.3522),
    ('Darri-Bolide Lyon Presqu ile', '74 Rue de la Republique', 'Lyon', '69002', '04 72 00 00 05', 'lyon@darri-bolide.fr', FALSE, 45.7640, 4.8357),
    ('Darri-Bolide Bordeaux Centre', '48 Cours de la Marne', 'Bordeaux', '33000', '05 56 00 00 02', 'bordeaux@darri-bolide.fr', FALSE, 44.8378, -0.5792)
) AS new_agences(nom, adresse, ville, code_postal, telephone, email, est_siege, latitude, longitude)
WHERE NOT EXISTS (
  SELECT 1
  FROM agences a
  WHERE a.email = new_agences.email
);

-- Marques
INSERT INTO marques (nom) VALUES
  ('Renault'), ('Peugeot'), ('Volkswagen'), ('BMW'), ('Tesla'), ('Toyota'), ('Audi'), ('Mercedes-Benz')
ON CONFLICT (nom) DO NOTHING;

-- Modeles
INSERT INTO modeles (marque_id, nom)
SELECT m.id, x.nom
FROM (VALUES
  ('Renault', 'Clio'),
  ('Renault', 'Megane'),
  ('Peugeot', '208'),
  ('Peugeot', '3008'),
  ('Volkswagen', 'Golf'),
  ('Volkswagen', 'Tiguan'),
  ('BMW', 'Serie 3'),
  ('BMW', 'X3'),
  ('Tesla', 'Model 3'),
  ('Tesla', 'Model Y'),
  ('Toyota', 'Yaris'),
  ('Toyota', 'Corolla'),
  ('Audi', 'A3'),
  ('Audi', 'Q5'),
  ('Mercedes-Benz', 'Classe A'),
  ('Mercedes-Benz', 'GLC')
) AS x(marque, nom)
JOIN marques m ON m.nom = x.marque
ON CONFLICT (marque_id, nom) DO NOTHING;

-- Utilisateurs de test
-- Password hash pour "Admin2024!"
INSERT INTO utilisateurs (prenom, nom, email, password_hash, role, agence_id)
SELECT
  'Admin', 'Darri-Bolide', 'admin@darri-bolide.fr',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhCanUXSmRbxPYuWLSiHcm',
  'admin', a.id
FROM agences a
ORDER BY a.id
LIMIT 1
ON CONFLICT (email) DO NOTHING;

-- Password hash pour "Vendeur2024!"
INSERT INTO utilisateurs (prenom, nom, email, password_hash, role, agence_id)
SELECT
  'Paul', 'Vendeur', 'vendeur@darri-bolide.fr',
  '$2b$12$FWvWZw6z1f4ckbozjzqFpuA7QqK7pBXf13v7yfq5zszT0tNV8v5B6',
  'vendeur', a.id
FROM agences a
ORDER BY a.id
LIMIT 1
ON CONFLICT (email) DO NOTHING;

-- Password hash pour "Client2024!"
INSERT INTO utilisateurs (prenom, nom, email, password_hash, role, agence_id)
VALUES
  ('Alice', 'Client', 'client@darri-bolide.fr',
   '$2b$12$UEN5DkzhJq50FgCYFsLhUuOX5PPTfL6A22L70v4A6i2F1H5qz2vby',
   'client', NULL)
ON CONFLICT (email) DO NOTHING;

-- Vehicules de demo
-- On dedoublonne par VIN pour permettre la relance.
WITH vendeur_ref AS (
  SELECT id AS vendeur_id FROM utilisateurs WHERE email = 'vendeur@darri-bolide.fr' LIMIT 1
),
agence_ref AS (
  SELECT id, row_number() OVER (ORDER BY id) AS rn FROM agences
),
vehicules_src AS (
  SELECT * FROM (VALUES
    ('Renault', 'Clio',        'Techno',            2023, 'occasion',      14990::numeric, NULL::numeric, 18000,  'essence',              'manuelle',         'Gris',   90,  'VF1CLIO0000000001', 'Citadine propre, entretien a jour, 1ere main.'),
    ('Peugeot', '208',         'Allure',            2022, 'occasion',      16200::numeric, 17900::numeric, 24000,  'essence',              'manuelle',         'Bleu',  100,  'VF320800000000002', 'Tres bon etat general, faible consommation.'),
    ('Volkswagen', 'Golf',     'Life',              2021, 'occasion',      21400::numeric, NULL::numeric, 39000,  'diesel',               'automatique',      'Noir',  115,  'WVWGOLF0000000003', 'Vehicule polyvalent et confortable.'),
    ('BMW', 'Serie 3',         'M Sport',           2020, 'occasion',      31900::numeric, 33900::numeric, 52000,  'hybride',              'automatique',      'Blanc', 190,  'WBA3SER0000000004', 'Finition sport, excellent etat.'),
    ('Tesla', 'Model 3',       'Propulsion',        2021, 'occasion',      33800::numeric, NULL::numeric, 27000,  'electrique',           'automatique',      'Rouge', 283,  '5YJ3MOD0000000005', 'Autonomie solide, historique clair.'),
    ('Toyota', 'Yaris',        'Dynamic',           2024, 'neuf',          22500::numeric, NULL::numeric,     0,  'hybride',              'automatique',      'Blanc', 116,  'JTDBYAR0000000006', 'Vehicule neuf, disponible immediatement.'),
    ('Audi', 'A3',             'S line',            2022, 'demonstrateur', 28900::numeric, 30900::numeric, 12000,  'essence',              'automatique',      'Gris',  150,  'WAUA3000000000007', 'Vehicule de demonstration tres bien equipe.'),
    ('Mercedes-Benz', 'GLC',   'Business Line',     2020, 'occasion',      39900::numeric, NULL::numeric, 61000,  'diesel',               'automatique',      'Noir',  194,  'W1NGLC00000000008', 'SUV premium, parfait pour la route.'),
    ('Peugeot', '3008',        'GT Pack',           2023, 'occasion',      32900::numeric, NULL::numeric, 15000,  'hybride_rechargeable', 'automatique',      'Gris',  225,  'VF330080000000009', 'Tres bien optionne, rechargeable.'),
    ('Renault', 'Megane',      'E-Tech',            2024, 'neuf',          35900::numeric, NULL::numeric,     0,  'electrique',           'automatique',      'Bleu',  220,  'VF1MEGA0000000010', 'Electrique recente, autonomie confortable.'),
    ('Toyota', 'Corolla',      'Design',            2021, 'occasion',      21900::numeric, NULL::numeric, 42000,  'hybride',              'automatique',      'Argent', 122, 'JTDCORO0000000011', 'Berline fiable et economique.'),
    ('BMW', 'X3',              'xDrive20d',         2019, 'occasion',      30900::numeric, NULL::numeric, 78000,  'diesel',               'automatique',      'Noir',  190,  'WBA0X300000000012', 'SUV spacieux, historique d entretien complet.')
  ) AS t(marque, modele, version, annee, etat, prix, prix_barre, kilometrage, energie, boite, couleur_ext, puissance_cv, vin, description)
),
vehicules_numbered AS (
  SELECT
    vs.*,
    row_number() OVER (ORDER BY vs.vin) AS rn
  FROM vehicules_src vs
)
INSERT INTO vehicules (
  agence_id, marque_id, modele_id, version, annee, etat, statut, prix, prix_barre,
  kilometrage, energie, boite, couleur_ext, puissance_cv, vin, description, vendeur_id
)
SELECT
  ar.id AS agence_id,
  ma.id AS marque_id,
  mo.id AS modele_id,
  vn.version,
  vn.annee,
  vn.etat::etat_vehicule,
  'disponible'::statut_vehicule,
  vn.prix,
  vn.prix_barre,
  vn.kilometrage,
  vn.energie::energie_vehicule,
  vn.boite::boite_vehicule,
  vn.couleur_ext,
  vn.puissance_cv,
  vn.vin,
  vn.description,
  vr.vendeur_id
FROM vehicules_numbered vn
JOIN marques ma ON ma.nom = vn.marque
JOIN modeles mo ON mo.nom = vn.modele AND mo.marque_id = ma.id
JOIN vendeur_ref vr ON TRUE
JOIN agence_ref ar ON ar.rn = ((vn.rn - 1) % (SELECT COUNT(*) FROM agence_ref)) + 1
ON CONFLICT (vin) DO NOTHING;

COMMIT;
