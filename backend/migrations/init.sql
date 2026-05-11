-- ============================================================
--  Darri-Bolide — Schéma de base de données PostgreSQL
--  init.sql
-- ============================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- ──────────────────────────────────────────────────────────────
--  TABLES RÉFÉRENTIELLES
-- ──────────────────────────────────────────────────────────────

CREATE TABLE agences (
    id            SERIAL PRIMARY KEY,
    nom           VARCHAR(100)  NOT NULL,
    adresse       VARCHAR(255)  NOT NULL,
    ville         VARCHAR(100)  NOT NULL,
    code_postal   VARCHAR(10)   NOT NULL,
    telephone     VARCHAR(20),
    email         VARCHAR(150),
    est_siege     BOOLEAN       DEFAULT FALSE,
    latitude      DECIMAL(9,6),
    longitude     DECIMAL(9,6),
    created_at    TIMESTAMP     DEFAULT NOW()
);

CREATE TABLE marques (
    id    SERIAL PRIMARY KEY,
    nom   VARCHAR(80) NOT NULL UNIQUE,
    logo  VARCHAR(255)
);

CREATE TABLE modeles (
    id        SERIAL PRIMARY KEY,
    marque_id INTEGER     NOT NULL REFERENCES marques(id) ON DELETE CASCADE,
    nom       VARCHAR(100) NOT NULL,
    UNIQUE (marque_id, nom)
);

-- ──────────────────────────────────────────────────────────────
--  UTILISATEURS
-- ──────────────────────────────────────────────────────────────

CREATE TYPE user_role AS ENUM ('client', 'vendeur', 'admin');

CREATE TABLE utilisateurs (
    id             SERIAL PRIMARY KEY,
    uuid           UUID          DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    prenom         VARCHAR(80)   NOT NULL,
    nom            VARCHAR(80)   NOT NULL,
    email          VARCHAR(150)  NOT NULL UNIQUE,
    telephone      VARCHAR(20),
    password_hash  VARCHAR(255)  NOT NULL,
    role           user_role     DEFAULT 'client',
    agence_id      INTEGER       REFERENCES agences(id) ON DELETE SET NULL,
    est_actif      BOOLEAN       DEFAULT TRUE,
    created_at     TIMESTAMP     DEFAULT NOW(),
    updated_at     TIMESTAMP     DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────
--  VÉHICULES
-- ──────────────────────────────────────────────────────────────

CREATE TYPE etat_vehicule  AS ENUM ('neuf', 'occasion', 'demonstrateur');
CREATE TYPE statut_vehicule AS ENUM ('disponible', 'reserve', 'vendu', 'archive');
CREATE TYPE energie_vehicule AS ENUM ('essence', 'diesel', 'electrique', 'hybride', 'hybride_rechargeable', 'gpl', 'autre');
CREATE TYPE boite_vehicule  AS ENUM ('manuelle', 'automatique', 'semi_automatique');

CREATE TABLE vehicules (
    id                SERIAL PRIMARY KEY,
    uuid              UUID           DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    agence_id         INTEGER        NOT NULL REFERENCES agences(id) ON DELETE RESTRICT,
    marque_id         INTEGER        NOT NULL REFERENCES marques(id) ON DELETE RESTRICT,
    modele_id         INTEGER        NOT NULL REFERENCES modeles(id) ON DELETE RESTRICT,
    version           VARCHAR(150),
    annee             SMALLINT       NOT NULL CHECK (annee BETWEEN 1980 AND 2030),
    etat              etat_vehicule  NOT NULL DEFAULT 'occasion',
    statut            statut_vehicule NOT NULL DEFAULT 'disponible',
    prix              NUMERIC(10,2)  NOT NULL CHECK (prix >= 0),
    prix_barre        NUMERIC(10,2),                         -- prix barré (avant remise)
    kilometrage       INTEGER        DEFAULT 0 CHECK (kilometrage >= 0),
    energie           energie_vehicule NOT NULL,
    boite             boite_vehicule NOT NULL,
    couleur_ext       VARCHAR(60),
    couleur_int       VARCHAR(60),
    nb_portes         SMALLINT,
    nb_places         SMALLINT,
    puissance_cv      SMALLINT,
    puissance_kw      SMALLINT,
    cylindree         SMALLINT,
    co2               SMALLINT,                              -- g/km
    consommation      DECIMAL(4,1),                          -- L/100km
    vin               VARCHAR(17) UNIQUE,
    description       TEXT,
    equipements       TEXT[],                                -- tableau d'équipements
    vendeur_id        INTEGER        REFERENCES utilisateurs(id) ON DELETE SET NULL,
    created_at        TIMESTAMP      DEFAULT NOW(),
    updated_at        TIMESTAMP      DEFAULT NOW()
);

CREATE TABLE photos_vehicules (
    id           SERIAL PRIMARY KEY,
    vehicule_id  INTEGER      NOT NULL REFERENCES vehicules(id) ON DELETE CASCADE,
    url          VARCHAR(500) NOT NULL,
    est_principale BOOLEAN    DEFAULT FALSE,
    ordre        SMALLINT     DEFAULT 0,
    created_at   TIMESTAMP    DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────
--  MESSAGERIE CLIENT ↔ GARAGE
-- ──────────────────────────────────────────────────────────────

CREATE TYPE statut_message AS ENUM ('ouvert', 'en_cours', 'resolu', 'ferme');
CREATE TYPE sujet_message  AS ENUM ('renseignement_vehicule', 'rendez_vous', 'reclamation', 'autre');

CREATE TABLE conversations (
    id           SERIAL PRIMARY KEY,
    uuid         UUID           DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    client_id    INTEGER        NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    agence_id    INTEGER        REFERENCES agences(id) ON DELETE SET NULL,
    vehicule_id  INTEGER        REFERENCES vehicules(id) ON DELETE SET NULL,
    sujet        sujet_message  NOT NULL DEFAULT 'autre',
    titre        VARCHAR(200)   NOT NULL,
    statut       statut_message DEFAULT 'ouvert',
    created_at   TIMESTAMP      DEFAULT NOW(),
    updated_at   TIMESTAMP      DEFAULT NOW()
);

CREATE TABLE messages (
    id               SERIAL PRIMARY KEY,
    conversation_id  INTEGER      NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    auteur_id        INTEGER      NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    contenu          TEXT         NOT NULL,
    est_lu           BOOLEAN      DEFAULT FALSE,
    created_at       TIMESTAMP    DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────
--  RENDEZ-VOUS
-- ──────────────────────────────────────────────────────────────

CREATE TYPE type_rdv    AS ENUM ('essai', 'entretien', 'reparation', 'expertise', 'livraison');
CREATE TYPE statut_rdv  AS ENUM ('confirme', 'en_attente', 'annule', 'effectue');

CREATE TABLE rendez_vous (
    id           SERIAL PRIMARY KEY,
    client_id    INTEGER      NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    agence_id    INTEGER      NOT NULL REFERENCES agences(id) ON DELETE RESTRICT,
    vehicule_id  INTEGER      REFERENCES vehicules(id) ON DELETE SET NULL,
    type_rdv     type_rdv     NOT NULL,
    statut       statut_rdv   DEFAULT 'en_attente',
    date_heure   TIMESTAMP    NOT NULL,
    duree_min    SMALLINT     DEFAULT 60,
    notes        TEXT,
    created_at   TIMESTAMP    DEFAULT NOW(),
    updated_at   TIMESTAMP    DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────
--  DEMANDES D'ESTIMATION (traitement manuel)
-- ──────────────────────────────────────────────────────────────
CREATE TABLE demandes_estimations (
    id                SERIAL PRIMARY KEY,
    marque            VARCHAR(120) NOT NULL,
    modele            VARCHAR(120) NOT NULL,
    annee             SMALLINT     NOT NULL,
    kilometrage       INTEGER      NOT NULL DEFAULT 0,
    energie           VARCHAR(30)  NOT NULL,
    email             VARCHAR(150) NOT NULL,
    statut            VARCHAR(20)  NOT NULL DEFAULT 'en_attente',
    commentaire_admin TEXT,
    created_at        TIMESTAMP    DEFAULT NOW(),
    updated_at        TIMESTAMP    DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────
--  FAVORIS & STATISTIQUES
-- ──────────────────────────────────────────────────────────────

CREATE TABLE favoris (
    utilisateur_id  INTEGER   NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    vehicule_id     INTEGER   NOT NULL REFERENCES vehicules(id) ON DELETE CASCADE,
    created_at      TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (utilisateur_id, vehicule_id)
);

CREATE TABLE vues_vehicules (
    id           SERIAL PRIMARY KEY,
    vehicule_id  INTEGER      NOT NULL REFERENCES vehicules(id) ON DELETE CASCADE,
    ip_address   INET,
    user_agent   TEXT,
    created_at   TIMESTAMP    DEFAULT NOW()
);

-- ──────────────────────────────────────────────────────────────
--  INDEX POUR LES PERFORMANCES
-- ──────────────────────────────────────────────────────────────

CREATE INDEX idx_vehicules_etat      ON vehicules(etat);
CREATE INDEX idx_vehicules_statut    ON vehicules(statut);
CREATE INDEX idx_vehicules_agence    ON vehicules(agence_id);
CREATE INDEX idx_vehicules_marque    ON vehicules(marque_id);
CREATE INDEX idx_vehicules_prix      ON vehicules(prix);
CREATE INDEX idx_vehicules_annee     ON vehicules(annee);
CREATE INDEX idx_vehicules_energie   ON vehicules(energie);
CREATE INDEX idx_photos_vehicule     ON photos_vehicules(vehicule_id);
CREATE INDEX idx_messages_conv       ON messages(conversation_id);
CREATE INDEX idx_conv_client         ON conversations(client_id);
CREATE INDEX idx_rdv_agence_date     ON rendez_vous(agence_id, date_heure);
CREATE INDEX idx_vues_vehicule       ON vues_vehicules(vehicule_id);
CREATE INDEX idx_demandes_estimation_statut ON demandes_estimations(statut);

-- ──────────────────────────────────────────────────────────────
--  TRIGGERS : updated_at automatique
-- ──────────────────────────────────────────────────────────────
-- ==================================================================
--  Données de démonstration / seed (sera inséré lors de l'initialisation)
-- ==================================================================

-- petites agences
INSERT INTO agences (nom, adresse, ville, code_postal, telephone, email, est_siege, latitude, longitude)
VALUES
  ('Agence Paris', '10 rue de Rivoli', 'Paris', '75001', '01 23 45 67 89', 'paris@darri-bolide.fr', TRUE, 48.8566, 2.3522),
  ('Agence Lyon',  '5 rue de la République', 'Lyon',  '69002', '04 78 00 00 00',     'lyon@darri-bolide.fr',  FALSE,45.7640, 4.8357);

-- marques et modèles de base
INSERT INTO marques (nom) VALUES ('Renault'), ('Peugeot'), ('Tesla');

INSERT INTO modeles (marque_id, nom)
SELECT id, 'Clio'    FROM marques WHERE nom = 'Renault'
UNION ALL
SELECT id, '208'     FROM marques WHERE nom = 'Peugeot'
UNION ALL
SELECT id, 'Model 3' FROM marques WHERE nom = 'Tesla';

-- quelques véhicules neufs et d'occasion
INSERT INTO vehicules (
    agence_id, marque_id, modele_id, annee, etat, statut,
    prix, kilometrage, energie, boite
)
VALUES
  (1, (SELECT id FROM marques WHERE nom='Renault'), (SELECT id FROM modeles WHERE nom='Clio'),    2022, 'neuf',     'disponible', 18500, 0,     'essence',   'manuelle'),
  (2, (SELECT id FROM marques WHERE nom='Peugeot'),(SELECT id FROM modeles WHERE nom='208'),     2018, 'occasion', 'disponible',  9500, 45000, 'diesel',    'manuelle'),
  (1, (SELECT id FROM marques WHERE nom='Tesla'),  (SELECT id FROM modeles WHERE nom='Model 3'),2019, 'occasion', 'disponible', 33800, 12000, 'electrique','automatique');

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_vehicules_updated
    BEFORE UPDATE ON vehicules
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_utilisateurs_updated
    BEFORE UPDATE ON utilisateurs
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_conversations_updated
    BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_rdv_updated
    BEFORE UPDATE ON rendez_vous
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_demandes_estimations_updated
    BEFORE UPDATE ON demandes_estimations
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ──────────────────────────────────────────────────────────────
--  VUE ANALYTIQUE : véhicules avec stats
-- ──────────────────────────────────────────────────────────────

CREATE VIEW v_vehicules_stats AS
SELECT
    v.id,
    v.uuid,
    ma.nom                             AS marque,
    mo.nom                             AS modele,
    v.version,
    v.annee,
    v.etat,
    v.statut,
    v.prix,
    v.kilometrage,
    v.energie,
    a.ville                            AS agence_ville,
    COUNT(DISTINCT vv.id)              AS nb_vues,
    COUNT(DISTINCT f.utilisateur_id)   AS nb_favoris,
    p.url                              AS photo_principale
FROM vehicules v
JOIN marques          ma ON ma.id = v.marque_id
JOIN modeles          mo ON mo.id = v.modele_id
JOIN agences          a  ON a.id  = v.agence_id
LEFT JOIN vues_vehicules vv ON vv.vehicule_id = v.id
LEFT JOIN favoris         f  ON f.vehicule_id  = v.id
LEFT JOIN photos_vehicules p  ON p.vehicule_id  = v.id AND p.est_principale = TRUE
GROUP BY v.id, ma.nom, mo.nom, a.ville, p.url;

-- ──────────────────────────────────────────────────────────────
--  DONNÉES INITIALES
-- ──────────────────────────────────────────────────────────────

-- Agences
INSERT INTO agences (nom, adresse, ville, code_postal, telephone, email, est_siege, latitude, longitude) VALUES
('Darri-Bolide Aix-en-Provence', '12 Avenue du Général de Gaulle', 'Aix-en-Provence', '13100', '04 42 00 00 01', 'aix@darri-bolide.fr', TRUE,  43.5297, 5.4474),
('Darri-Bolide Bordeaux',        '48 Cours de la Marne',           'Bordeaux',        '33000', '05 56 00 00 02', 'bordeaux@darri-bolide.fr', FALSE, 44.8378, -0.5792),
('Darri-Bolide Paris 15e',       '22 Rue Lecourbe',                'Paris',           '75015', '01 40 00 00 03', 'paris15@darri-bolide.fr', FALSE, 48.8416, 2.3058),
('Darri-Bolide Paris 8e',        '5 Avenue de Friedland',          'Paris',           '75008', '01 40 00 00 04', 'paris8@darri-bolide.fr',  FALSE, 48.8744, 2.3019),
('Darri-Bolide Lyon',            '74 Rue de la République',        'Lyon',            '69002', '04 72 00 00 05', 'lyon@darri-bolide.fr',    FALSE, 45.7640, 4.8357),
('Darri-Bolide Marseille',       '30 Boulevard Périer',            'Marseille',       '13008', '04 91 00 00 06', 'marseille@darri-bolide.fr', FALSE, 43.2965, 5.3698),
('Darri-Bolide Toulouse',        '15 Allée Jean Jaurès',           'Toulouse',        '31000', '05 61 00 00 07', 'toulouse@darri-bolide.fr', FALSE, 43.6047, 1.4442),
('Darri-Bolide Montpellier',     '8 Avenue de Lodève',             'Montpellier',     '34000', '04 67 00 00 08', 'montpellier@darri-bolide.fr', FALSE, 43.6119, 3.8772),
('Darri-Bolide Nice',            '54 Avenue Jean Médecin',         'Nice',            '06000', '04 93 00 00 09', 'nice@darri-bolide.fr',    FALSE, 43.7102, 7.2620),
('Darri-Bolide Nantes',          '20 Boulevard des Martyrs',       'Nantes',          '44000', '02 40 00 00 10', 'nantes@darri-bolide.fr',  FALSE, 47.2184, -1.5536),
('Darri-Bolide Strasbourg',      '3 Rue du Dôme',                  'Strasbourg',      '67000', '03 88 00 00 11', 'strasbourg@darri-bolide.fr', FALSE, 48.5734, 7.7521),
('Darri-Bolide Rennes',          '16 Rue Saint-Hélier',            'Rennes',          '35000', '02 99 00 00 12', 'rennes@darri-bolide.fr',  FALSE, 48.1173, -1.6778),
('Darri-Bolide Lille',           '60 Rue Nationale',               'Lille',           '59000', '03 20 00 00 13', 'lille@darri-bolide.fr',   FALSE, 50.6292, 3.0573);

-- Marques
INSERT INTO marques (nom) VALUES
('Renault'), ('Peugeot'), ('Citroën'), ('Volkswagen'), ('BMW'),
('Mercedes-Benz'), ('Audi'), ('Toyota'), ('Honda'), ('Ford'),
('Kia'), ('Hyundai'), ('Tesla'), ('Volvo'), ('Porsche');

-- Modèles
INSERT INTO modeles (marque_id, nom) VALUES
(1, 'Clio'), (1, 'Mégane'), (1, 'Kadjar'), (1, 'Zoe'),
(2, '208'), (2, '3008'), (2, '508'),
(3, 'C3'), (3, 'C5 Aircross'),
(4, 'Golf'), (4, 'Tiguan'), (4, 'Polo'), (4, 'ID.4'),
(5, 'Série 3'), (5, 'Série 5'), (5, 'X3'), (5, 'X5'),
(6, 'Classe A'), (6, 'Classe C'), (6, 'GLC'),
(7, 'A3'), (7, 'A4'), (7, 'Q5'),
(8, 'Corolla'), (8, 'RAV4'), (8, 'Yaris'),
(13, 'Model 3'), (13, 'Model Y');

-- Admin par défaut (password: Admin2024!)
INSERT INTO utilisateurs (prenom, nom, email, password_hash, role, agence_id) VALUES
('Admin', 'Darri-Bolide', 'admin@darri-bolide.fr',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMqJqhCanUXSmRbxPYuWLSiHcm',
 'admin', 1);
