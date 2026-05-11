from flask import Blueprint, jsonify
from app.models.agence import Agence, Marque

bp = Blueprint("agences", __name__)


@bp.get("/")
def list_agences():
    agences = Agence.query.order_by(Agence.est_siege.desc(), Agence.ville).all()
    return jsonify([a.to_dict() for a in agences]), 200


@bp.get("/<int:agence_id>")
def get_agence(agence_id):
    a = Agence.query.get_or_404(agence_id)
    data = a.to_dict()
    data["nb_vehicules"] = a.vehicules.filter_by(statut="disponible").count()
    return jsonify(data), 200
