#!/usr/bin/env python3
import os
from pathlib import Path

import psycopg2
from PIL import Image, ImageDraw
from dotenv import load_dotenv


def parse_database_name(database_url: str) -> str:
    # Format attendu: postgresql://user:pass@host:port/dbname
    return database_url.rsplit("/", 1)[-1]


def main() -> None:
    load_dotenv()

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://darri_user:darri_pass@localhost:5432/darri_bolide_dev",
    )
    upload_root = Path(os.getenv("UPLOAD_FOLDER", "/var/www/darri-bolide/uploads"))
    vehicules_root = upload_root / "vehicules"
    vehicules_root.mkdir(parents=True, exist_ok=True)

    conn = psycopg2.connect(database_url)
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT v.id, v.uuid, ma.nom, mo.nom
                FROM vehicules v
                JOIN marques ma ON ma.id = v.marque_id
                JOIN modeles mo ON mo.id = v.modele_id
                WHERE v.statut <> 'archive'
                ORDER BY v.id
                """
            )
            vehicules = cur.fetchall()

            created = 0
            linked = 0

            for vehicule_id, uuid, marque, modele in vehicules:
                cur.execute(
                    "SELECT COUNT(*) FROM photos_vehicules WHERE vehicule_id = %s",
                    (vehicule_id,),
                )
                if cur.fetchone()[0] > 0:
                    continue

                folder = vehicules_root / str(vehicule_id)
                folder.mkdir(parents=True, exist_ok=True)
                filename = f"{uuid}_main.webp"
                filepath = folder / filename

                # Image de demo simple mais exploitable visuellement.
                img = Image.new("RGB", (1200, 800), color=(20, 20, 20))
                draw = ImageDraw.Draw(img)
                draw.rectangle([(40, 40), (1160, 760)], outline=(220, 20, 60), width=8)
                draw.rectangle([(70, 70), (1130, 730)], outline=(255, 255, 255), width=2)
                draw.text((110, 180), "DARRI-BOLIDE", fill=(220, 20, 60))
                draw.text((110, 300), f"{marque} {modele}", fill=(245, 245, 245))
                draw.text((110, 380), "Photo de demonstration", fill=(180, 180, 180))
                img.save(filepath, "WEBP", quality=90)

                url = f"/uploads/vehicules/{vehicule_id}/{filename}"
                cur.execute(
                    """
                    INSERT INTO photos_vehicules (vehicule_id, url, est_principale, ordre)
                    VALUES (%s, %s, TRUE, 0)
                    """,
                    (vehicule_id, url),
                )
                created += 1
                linked += 1

        conn.commit()
        print(f"Images creees: {created}")
        print(f"Photos liees en base: {linked}")
        print(f"Base cible: {parse_database_name(database_url)}")
        print(f"Dossier uploads: {vehicules_root}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
