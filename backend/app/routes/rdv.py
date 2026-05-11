from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.rendez_vous import RendezVous
from app.models.utilisateur import Utilisateur

bp = Blueprint("rdv", __name__)


def current_user():
    return Utilisateur.query.get(int(get_jwt_identity()))


@bp.post("/")
@jwt_required()
def create_rdv():
    user = current_user()
    data = request.get_json()
    required = ("agence_id", "type_rdv", "date_heure")
    if not all(data.get(f) for f in required):
        return jsonify({"error": "Champs obligatoires manquants"}), 400

    try:
        dt = datetime.fromisoformat(data["date_heure"])
    except ValueError:
        return jsonify({"error": "Format date invalide (ISO 8601)"}), 400

    rdv = RendezVous(
        client_id   = user.id,
        agence_id   = int(data["agence_id"]),
        vehicule_id = data.get("vehicule_id"),
        type_rdv    = data["type_rdv"],
        date_heure  = dt,
        duree_min   = int(data.get("duree_min", 60)),
        notes       = data.get("notes"),
    )
    db.session.add(rdv)
    db.session.commit()
    return jsonify(rdv.to_dict()), 201


@bp.get("/")
@jwt_required()
def list_rdv():
    user = current_user()
    if user.role in ("vendeur", "admin"):
        rdvs = RendezVous.query.filter_by(agence_id=user.agence_id)\
                    .order_by(RendezVous.date_heure).all()
    else:
        rdvs = RendezVous.query.filter_by(client_id=user.id)\
                    .order_by(RendezVous.date_heure).all()
    return jsonify([r.to_dict() for r in rdvs]), 200


@bp.patch("/<int:rdv_id>/statut")
@jwt_required()
def update_statut(rdv_id):
    user = current_user()
    rdv  = RendezVous.query.get_or_404(rdv_id)

    # Le client peut seulement annuler son propre RDV
    if user.role == "client":
        if rdv.client_id != user.id:
            return jsonify({"error": "Accès interdit"}), 403
        new_statut = "annule"
    else:
        new_statut = request.get_json().get("statut", "confirme")

    rdv.statut = new_statut
    db.session.commit()
    return jsonify(rdv.to_dict()), 200
