#!/usr/bin/env python3
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def download_model_image(dest_path: Path, marque: str, modele: str) -> None:
    keywords = f"{marque},{modele},car"
    urls = [
        f"https://loremflickr.com/1200/800/{urllib.parse.quote_plus(keywords)}",
        "https://loremflickr.com/1200/800/car",
    ]
    last_error = None
    for url in urls:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read()
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_bytes(data)
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(f"Echec telechargement image pour {marque} {modele}: {last_error}")


def main() -> None:
    load_dotenv()
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://darri_user:darri_pass@localhost:5432/darri_bolide_dev",
    )
    upload_root = Path(os.getenv("UPLOAD_FOLDER", "/var/www/darri-bolide/uploads"))
    images_cache = upload_root / "modeles"
    vehicules_root = upload_root / "vehicules"
    images_cache.mkdir(parents=True, exist_ok=True)
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

            model_to_cache = {}
            created_files = 0
            linked = 0

            for vehicule_id, uuid, marque, modele in vehicules:
                model_key = (marque, modele)
                if model_key not in model_to_cache:
                    filename = f"{slugify(marque)}-{slugify(modele)}.jpg"
                    model_img_path = images_cache / filename
                    if not model_img_path.exists():
                        download_model_image(model_img_path, marque, modele)
                        created_files += 1
                    model_to_cache[model_key] = model_img_path

                model_img_path = model_to_cache[model_key]
                vehicule_dir = vehicules_root / str(vehicule_id)
                vehicule_dir.mkdir(parents=True, exist_ok=True)
                vehicule_filename = f"{uuid}_main.jpg"
                vehicule_path = vehicule_dir / vehicule_filename
                vehicule_path.write_bytes(model_img_path.read_bytes())

                url = f"/uploads/vehicules/{vehicule_id}/{vehicule_filename}"
                cur.execute(
                    """
                    SELECT id FROM photos_vehicules
                    WHERE vehicule_id = %s
                    ORDER BY est_principale DESC, ordre ASC, id ASC
                    LIMIT 1
                    """,
                    (vehicule_id,),
                )
                row = cur.fetchone()
                if row:
                    cur.execute(
                        """
                        UPDATE photos_vehicules
                        SET url = %s, est_principale = TRUE, ordre = 0
                        WHERE id = %s
                        """,
                        (url, row[0]),
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO photos_vehicules (vehicule_id, url, est_principale, ordre)
                        VALUES (%s, %s, TRUE, 0)
                        """,
                        (vehicule_id, url),
                    )
                linked += 1

        conn.commit()
        print(f"Images modele telechargees: {created_files}")
        print(f"Annonces mises a jour: {linked}")
        print(f"Cache modeles: {images_cache}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
