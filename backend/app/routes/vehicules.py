import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from sqlalchemy import and_, or_

from app import db
from app.models.vehicule    import Vehicule, PhotoVehicule
from app.models.agence      import Marque, Modele
from app.models.utilisateur import Utilisateur

bp = Blueprint("vehicules", __name__)

ALLOWED = {"jpg", "jpeg", "png", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED


def require_role(*roles):
    """Décorateur interne pour vérifier le rôle JWT."""
    from functools import wraps
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            uid  = int(get_jwt_identity())
            user = Utilisateur.query.get(uid)
            if not user or user.role not in roles:
                return jsonify({"error": "Accès interdit"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ── GET /api/vehicules  (liste avec filtres & pagination) ─────
@bp.get("/")
def list_vehicules():
    q = Vehicule.query.filter(Vehicule.statut != "archive")

    # Filtres
    etat     = request.args.get("etat")         # neuf | occasion
    marque   = request.args.get("marque")
    agence   = request.args.get("agence_id", type=int)
    energie  = request.args.get("energie")
    prix_min = request.args.get("prix_min", type=float)
    prix_max = request.args.get("prix_max", type=float)
    km_max   = request.args.get("km_max",   type=int)
    annee_min= request.args.get("annee_min", type=int)
    statut   = request.args.get("statut", "disponible")
    search   = request.args.get("q", "").strip()

    if etat:
        q = q.filter(Vehicule.etat == etat)
    if statut:
        q = q.filter(Vehicule.statut == statut)
    if agence:
        q = q.filter(Vehicule.agence_id == agence)
    if energie:
        q = q.filter(Vehicule.energie == energie)
    if prix_min is not None:
        q = q.filter(Vehicule.prix >= prix_min)
    if prix_max is not None:
        q = q.filter(Vehicule.prix <= prix_max)
    if km_max is not None:
        q = q.filter(Vehicule.kilometrage <= km_max)
    if annee_min:
        q = q.filter(Vehicule.annee >= annee_min)
    if marque:
        q = q.join(Marque).filter(Marque.nom.ilike(f"%{marque}%"))
    if search:
        q = q.join(Marque).join(Modele).filter(
            or_(
                Marque.nom.ilike(f"%{search}%"),
                Modele.nom.ilike(f"%{search}%"),
                Vehicule.version.ilike(f"%{search}%"),
            )
        )

    # Tri
    sort = request.args.get("sort", "created_at_desc")
    sort_map = {
        "prix_asc":        Vehicule.prix.asc(),
        "prix_desc":       Vehicule.prix.desc(),
        "annee_desc":      Vehicule.annee.desc(),
        "km_asc":          Vehicule.kilometrage.asc(),
        "created_at_desc": Vehicule.created_at.desc(),
    }
    q = q.order_by(sort_map.get(sort, Vehicule.created_at.desc()))

    # Pagination
    page     = request.args.get("page",     1,  type=int)
    per_page = request.args.get("per_page", 12, type=int)
    per_page = min(per_page, 50)

    pagination = q.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items":    [v.to_dict() for v in pagination.items],
        "total":    pagination.total,
        "page":     page,
        "per_page": per_page,
        "pages":    pagination.pages,
    }), 200


# ── GET /api/vehicules/<uuid> ─────────────────────────────────
@bp.get("/<string:uuid>")
def get_vehicule(uuid):
    v = Vehicule.query.filter_by(uuid=uuid).first_or_404()

    # Enregistrer la vue
    from app.models.vehicule import PhotoVehicule
    from sqlalchemy import text
    try:
        db.session.execute(
            text("INSERT INTO vues_vehicules (vehicule_id, ip_address) VALUES (:vid, :ip)"),
            {"vid": v.id, "ip": request.remote_addr}
        )
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify(v.to_dict(full=True)), 200


# ── POST /api/vehicules  (vendeur ou admin) ───────────────────
@bp.post("/")
@require_role("vendeur", "admin")
def create_vehicule():
    data = request.get_json()
    required = ("agence_id", "marque_id", "modele_id", "annee",
                 "etat", "prix", "energie", "boite")
    if not all(data.get(f) for f in required):
        return jsonify({"error": "Champs obligatoires manquants"}), 400

    uid = int(get_jwt_identity())
    v = Vehicule(
        agence_id    = data["agence_id"],
        marque_id    = data["marque_id"],
        modele_id    = data["modele_id"],
        version      = data.get("version"),
        annee        = int(data["annee"]),
        etat         = data["etat"],
        statut       = data.get("statut", "disponible"),
        prix         = float(data["prix"]),
        prix_barre   = float(data["prix_barre"]) if data.get("prix_barre") else None,
        kilometrage  = int(data.get("kilometrage", 0)),
        energie      = data["energie"],
        boite        = data["boite"],
        couleur_ext  = data.get("couleur_ext"),
        couleur_int  = data.get("couleur_int"),
        nb_portes    = data.get("nb_portes"),
        nb_places    = data.get("nb_places"),
        puissance_cv = data.get("puissance_cv"),
        co2          = data.get("co2"),
        vin          = data.get("vin"),
        description  = data.get("description"),
        equipements  = data.get("equipements", []),
        vendeur_id   = uid,
    )
    db.session.add(v)
    db.session.commit()
    return jsonify(v.to_dict(full=True)), 201


# ── PUT /api/vehicules/<uuid> ─────────────────────────────────
@bp.put("/<string:uuid>")
@require_role("vendeur", "admin")
def update_vehicule(uuid):
    v    = Vehicule.query.filter_by(uuid=uuid).first_or_404()
    data = request.get_json()
    editable = (
        "version", "statut", "prix", "prix_barre", "kilometrage",
        "description", "equipements", "couleur_ext", "couleur_int",
        "nb_portes", "nb_places", "puissance_cv", "co2", "consommation",
    )
    for field in editable:
        if field in data:
            setattr(v, field, data[field])
    db.session.commit()
    return jsonify(v.to_dict(full=True)), 200


# ── DELETE /api/vehicules/<uuid>  (archive seulement) ─────────
@bp.delete("/<string:uuid>")
@jwt_required()
def delete_vehicule(uuid):
    v = Vehicule.query.filter_by(uuid=uuid).first_or_404()

    uid = int(get_jwt_identity())
    user = Utilisateur.query.get(uid)
    if not user:
        return jsonify({"error": "Accès interdit"}), 403

    # Admin can archive any véhicule; a vendeur can archive only their own annonces
    if user.role != "admin" and v.vendeur_id != user.id:
        return jsonify({"error": "Accès interdit"}), 403

    v.statut = "archive"
    db.session.commit()
    return jsonify({"message": "Véhicule archivé"}), 200


# ── POST /api/vehicules/<uuid>/photos ─────────────────────────
@bp.post("/<string:uuid>/photos")
@require_role("vendeur", "admin")
def upload_photo(uuid):
    v = Vehicule.query.filter_by(uuid=uuid).first_or_404()

    if "file" not in request.files:
        return jsonify({"error": "Aucun fichier envoyé"}), 400
    file = request.files["file"]
    if not allowed_file(file.filename):
        return jsonify({"error": "Format non autorisé (jpg, jpeg, png, webp)"}), 400

    filename  = secure_filename(file.filename)
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "vehicules", str(v.id))
    os.makedirs(save_path, exist_ok=True)

    unique_name = f"{uuid}_{filename}"
    file.save(os.path.join(save_path, unique_name))
    url = f"/uploads/vehicules/{v.id}/{unique_name}"

    is_principale = not v.photos  # première photo = principale
    photo = PhotoVehicule(
        vehicule_id    = v.id,
        url            = url,
        est_principale = is_principale,
        ordre          = len(v.photos),
    )
    db.session.add(photo)
    db.session.commit()
    return jsonify(photo.to_dict()), 201


# ── GET /api/vehicules/marques ────────────────────────────────
@bp.get("/marques/list")
def list_marques():
    marques = Marque.query.order_by(Marque.nom).all()
    return jsonify([m.to_dict() for m in marques]), 200


# ── GET /api/vehicules/stats ──────────────────────────────────
@bp.get("/stats/summary")
@require_role("vendeur", "admin")
def stats_summary():
    from sqlalchemy import func
    total     = Vehicule.query.filter(Vehicule.statut != "archive").count()
    neufs     = Vehicule.query.filter_by(etat="neuf",     statut="disponible").count()
    occasions = Vehicule.query.filter_by(etat="occasion", statut="disponible").count()
    vendus    = Vehicule.query.filter_by(statut="vendu").count()
    reserves  = Vehicule.query.filter_by(statut="reserve").count()

    prix_moy = db.session.query(
        func.avg(Vehicule.prix)
    ).filter(Vehicule.statut == "disponible").scalar()

    return jsonify({
        "total":          total,
        "neufs":          neufs,
        "occasions":      occasions,
        "vendus":         vendus,
        "reserves":       reserves,
        "prix_moyen":     round(float(prix_moy), 2) if prix_moy else 0,
    }), 200


@bp.get("/modeles/")
def list_modeles():
    marque_id = request.args.get("marque_id", type=int)
    q = Modele.query
    if marque_id:
        q = q.filter_by(marque_id=marque_id)
    return jsonify([m.to_dict() for m in q.order_by(Modele.nom).all()]), 200


# ── POST /api/vehicules/estimate ──────────────────────────────
@bp.post("/estimate")
def estimate_vehicule():
    """Simple estimation de valeur de revente basée sur l'âge et le kilométrage.

    Le front-end envoie un JSON contenant au moins ``annee`` et ``kilometrage``
    (les autres champs peuvent être fournis mais ne sont pas utilisés pour
    l'instant). Nous appliquons une dépréciation exponentielle de 15 % par
    année plus une réduction linéaire selon les kilomètres.
    """
    data = request.get_json() or {}
    try:
        annee = int(data.get("annee", 0))
        km = int(data.get("kilometrage", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Champs 'annee' ou 'kilometrage' invalides"}), 400

    from datetime import date
    age = max(0, date.today().year - annee)
    base_price = 25000.0
    estimation = base_price * (0.85 ** age) - (km * 0.05)
    estimation = max(estimation, 0.0)
    return jsonify({"estimate": round(estimation, 2)}), 200
