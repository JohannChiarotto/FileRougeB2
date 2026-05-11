"""
analyse_ventes.py
─────────────────
Script d'analyse et de prévision des ventes Darri-Bolide.
Utilise pandas + scikit-learn pour :
  - nettoyer les données de ventes
  - produire des rapports CSV/JSON
  - prédire les ventes futures par agence
  - identifier les véhicules et zones populaires

Usage :
    python analyse_ventes.py --db postgresql://user:pass@host/db --output ./reports
"""

import argparse
import json
import os
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


# ──────────────────────────────────────────────────────────────
#  EXTRACTION DEPUIS LA BASE
# ──────────────────────────────────────────────────────────────

QUERY_VENTES = text("""
    SELECT
        v.id                     AS vehicule_id,
        ma.nom                   AS marque,
        mo.nom                   AS modele,
        v.etat,
        v.energie,
        v.prix,
        v.kilometrage,
        v.annee,
        a.ville                  AS agence_ville,
        a.id                     AS agence_id,
        v.updated_at             AS date_vente
    FROM vehicules v
    JOIN marques  ma ON ma.id = v.marque_id
    JOIN modeles  mo ON mo.id = v.modele_id
    JOIN agences   a ON a.id  = v.agence_id
    WHERE v.statut = 'vendu'
    ORDER BY v.updated_at
""")

QUERY_VUES = text("""
    SELECT
        v.id   AS vehicule_id,
        ma.nom AS marque,
        mo.nom AS modele,
        a.ville,
        COUNT(vv.id) AS nb_vues
    FROM vues_vehicules vv
    JOIN vehicules  v  ON v.id  = vv.vehicule_id
    JOIN marques   ma  ON ma.id = v.marque_id
    JOIN modeles   mo  ON mo.id = v.modele_id
    JOIN agences    a  ON a.id  = v.agence_id
    GROUP BY v.id, ma.nom, mo.nom, a.ville
    ORDER BY nb_vues DESC
""")


def extract_data(engine):
    """Extrait les données de ventes et de consultations."""
    with engine.connect() as conn:
        df_ventes = pd.read_sql(QUERY_VENTES, conn)
        df_vues   = pd.read_sql(QUERY_VUES,   conn)
    return df_ventes, df_vues


# ──────────────────────────────────────────────────────────────
#  NETTOYAGE
# ──────────────────────────────────────────────────────────────

def clean_ventes(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et enrichit le DataFrame de ventes."""

    # Suppression des doublons
    df = df.drop_duplicates(subset="vehicule_id")

    # Conversion dates
    df["date_vente"] = pd.to_datetime(df["date_vente"], errors="coerce")
    df = df.dropna(subset=["date_vente"])

    # Variables temporelles
    df["annee_vente"]    = df["date_vente"].dt.year
    df["mois_vente"]     = df["date_vente"].dt.month
    df["trimestre"]      = df["date_vente"].dt.quarter
    df["nom_mois"]       = df["date_vente"].dt.strftime("%B")

    # Nettoyage prix et km
    df["prix"]         = pd.to_numeric(df["prix"],         errors="coerce")
    df["kilometrage"]  = pd.to_numeric(df["kilometrage"],  errors="coerce").fillna(0)
    df = df[df["prix"] > 0]

    # Catégories de prix
    df["tranche_prix"] = pd.cut(
        df["prix"],
        bins=[0, 10_000, 20_000, 35_000, 60_000, np.inf],
        labels=["<10k", "10-20k", "20-35k", "35-60k", ">60k"]
    )

    return df


# ──────────────────────────────────────────────────────────────
#  RAPPORTS
# ──────────────────────────────────────────────────────────────

def rapport_ventes_par_agence(df: pd.DataFrame) -> dict:
    """CA et volume par agence."""
    grp = df.groupby("agence_ville").agg(
        nb_ventes   = ("vehicule_id", "count"),
        ca_total    = ("prix",        "sum"),
        prix_moyen  = ("prix",        "mean"),
        prix_median = ("prix",        "median"),
    ).reset_index()
    grp = grp.sort_values("ca_total", ascending=False)
    return grp.round(2).to_dict(orient="records")


def rapport_marques_populaires(df: pd.DataFrame, top: int = 10) -> dict:
    """Marques les plus vendues."""
    grp = df.groupby("marque").agg(
        nb_ventes  = ("vehicule_id", "count"),
        prix_moyen = ("prix",        "mean"),
    ).reset_index().sort_values("nb_ventes", ascending=False).head(top)
    return grp.round(2).to_dict(orient="records")


def rapport_energie(df: pd.DataFrame) -> dict:
    """Répartition par type d'énergie."""
    grp = df.groupby("energie").agg(
        nb_ventes  = ("vehicule_id", "count"),
        pct        = ("vehicule_id", lambda x: round(len(x)/len(df)*100, 1)),
    ).reset_index().sort_values("nb_ventes", ascending=False)
    return grp.to_dict(orient="records")


def rapport_mensuel(df: pd.DataFrame) -> dict:
    """Ventes mensuelles pour la dernière année."""
    last_year = df["date_vente"].max() - pd.DateOffset(years=1)
    df_year   = df[df["date_vente"] >= last_year].copy()
    grp = df_year.groupby(["annee_vente", "mois_vente"]).agg(
        nb_ventes  = ("vehicule_id", "count"),
        ca         = ("prix",        "sum"),
    ).reset_index().sort_values(["annee_vente", "mois_vente"])
    return grp.round(2).to_dict(orient="records")


def zones_interessantes(df: pd.DataFrame, df_vues: pd.DataFrame) -> dict:
    """
    Identifie les zones (villes) avec le meilleur potentiel :
    fort taux de consultation ET faible concurrence (peu de ventes actuelles).
    """
    ventes_par_ville = df.groupby("agence_ville")["vehicule_id"].count().rename("ventes")
    vues_par_ville   = df_vues.groupby("ville")["nb_vues"].sum().rename("vues")

    merged = pd.concat([ventes_par_ville, vues_par_ville], axis=1).fillna(0)
    merged["score_potentiel"] = (
        merged["vues"] / (merged["ventes"] + 1)
    ).round(2)
    merged = merged.sort_values("score_potentiel", ascending=False)
    merged.index.name = "ville"
    return merged.reset_index().to_dict(orient="records")


# ──────────────────────────────────────────────────────────────
#  PRÉVISIONS (régression linéaire simple par agence)
# ──────────────────────────────────────────────────────────────

def previsions_ventes(df: pd.DataFrame, mois_futur: int = 3) -> dict:
    """
    Prédit les ventes des prochains mois par agence
    à l'aide d'une régression linéaire sur l'historique mensuel.
    """
    resultats = {}

    for agence, group in df.groupby("agence_ville"):
        mensuel = group.groupby(["annee_vente", "mois_vente"]).size().reset_index(name="ventes")
        if len(mensuel) < 4:
            continue  # pas assez de données

        # Feature : index de temps (mois séquentiels)
        mensuel["t"] = range(len(mensuel))
        X = mensuel[["t"]].values
        y = mensuel["ventes"].values

        model = LinearRegression()
        model.fit(X, y)

        # Prévisions pour les prochains mois
        t_max = mensuel["t"].max()
        previsions = []
        for i in range(1, mois_futur + 1):
            t_next = t_max + i
            pred   = max(0, round(float(model.predict([[t_next]])[0])))
            previsions.append({
                "mois":   i,
                "ventes": pred,
            })

        # Score de confiance (R²)
        r2 = round(model.score(X, y), 3)
        resultats[agence] = {
            "historique_nb_mois": len(mensuel),
            "r2_score":           r2,
            "previsions":         previsions,
        }

    return resultats


# ──────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Analyse ventes Darri-Bolide")
    parser.add_argument("--db",     required=True, help="URL PostgreSQL")
    parser.add_argument("--output", default="./reports", help="Dossier de sortie")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    engine = create_engine(args.db)

    print("⏳ Extraction des données...")
    df_ventes_raw, df_vues = extract_data(engine)

    print("🧹 Nettoyage...")
    df = clean_ventes(df_ventes_raw)
    print(f"   → {len(df)} ventes valides chargées.")

    if df.empty:
        print("⚠️  Aucune vente trouvée. Vérifiez la base de données.")
        return

    # Rapports
    rapports = {
        "ventes_par_agence":     rapport_ventes_par_agence(df),
        "marques_populaires":    rapport_marques_populaires(df),
        "repartition_energie":   rapport_energie(df),
        "evolution_mensuelle":   rapport_mensuel(df),
        "zones_potentiel":       zones_interessantes(df, df_vues),
        "previsions_3_mois":     previsions_ventes(df, mois_futur=3),
        "genere_le":             datetime.now().isoformat(),
    }

    # Export JSON
    json_path = os.path.join(args.output, "rapport_ventes.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rapports, f, ensure_ascii=False, indent=2)
    print(f"✅ Rapport JSON exporté : {json_path}")

    # Export CSV (ventes nettoyées)
    csv_path = os.path.join(args.output, "ventes_clean.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"✅ CSV ventes exporté    : {csv_path}")

    # Résumé console
    print("\n── RÉSUMÉ ─────────────────────────────────────")
    print(f"Total ventes   : {len(df)}")
    print(f"CA total       : {df['prix'].sum():,.0f} €")
    print(f"Prix moyen     : {df['prix'].mean():,.0f} €")
    print(f"Marque top     : {rapports['marques_populaires'][0]['marque'] if rapports['marques_populaires'] else 'N/A'}")
    print(f"Agence top CA  : {rapports['ventes_par_agence'][0]['agence_ville'] if rapports['ventes_par_agence'] else 'N/A'}")
    print("───────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()
