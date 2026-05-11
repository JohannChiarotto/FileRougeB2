from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.message     import Conversation, Message
from app.models.utilisateur import Utilisateur

bp = Blueprint("messages", __name__)


def current_user():
    return Utilisateur.query.get(int(get_jwt_identity()))


# ── GET /api/messages/conversations ──────────────────────────
@bp.get("/conversations")
@jwt_required()
def list_conversations():
    user = current_user()
    if user.role in ("vendeur", "admin"):
        convs = Conversation.query.filter_by(agence_id=user.agence_id)\
                    .order_by(Conversation.updated_at.desc()).all()
    else:
        convs = Conversation.query.filter_by(client_id=user.id)\
                    .order_by(Conversation.updated_at.desc()).all()
    return jsonify([c.to_dict() for c in convs]), 200


# ── POST /api/messages/conversations ─────────────────────────
@bp.post("/conversations")
@jwt_required()
def create_conversation():
    user = current_user()
    data = request.get_json()

    if not data.get("titre"):
        return jsonify({"error": "Titre obligatoire"}), 400

    conv = Conversation(
        client_id   = user.id,
        agence_id   = data.get("agence_id"),
        vehicule_id = data.get("vehicule_id"),
        sujet       = data.get("sujet", "autre"),
        titre       = data["titre"],
    )
    db.session.add(conv)
    db.session.flush()

    # Premier message
    if data.get("message"):
        msg = Message(
            conversation_id = conv.id,
            auteur_id       = user.id,
            contenu         = data["message"],
        )
        db.session.add(msg)

    db.session.commit()
    return jsonify(conv.to_dict(with_messages=True)), 201


# ── GET /api/messages/conversations/<id> ─────────────────────
@bp.get("/conversations/<int:conv_id>")
@jwt_required()
def get_conversation(conv_id):
    user = current_user()
    conv = Conversation.query.get_or_404(conv_id)

    # Vérification d'accès
    if user.role == "client" and conv.client_id != user.id:
        return jsonify({"error": "Accès interdit"}), 403

    # Marquer tous les messages comme lus
    Message.query.filter_by(conversation_id=conv_id, est_lu=False)\
                 .filter(Message.auteur_id != user.id)\
                 .update({"est_lu": True})
    db.session.commit()

    return jsonify(conv.to_dict(with_messages=True)), 200


# ── POST /api/messages/conversations/<id>/messages ───────────
@bp.post("/conversations/<int:conv_id>")
@jwt_required()
def send_message(conv_id):
    user = current_user()
    conv = Conversation.query.get_or_404(conv_id)

    if conv.statut in ("ferme", "resolu") and user.role == "client":
        return jsonify({"error": "Cette conversation est fermée"}), 400

    data = request.get_json()
    if not data.get("contenu"):
        return jsonify({"error": "Contenu vide"}), 400

    msg = Message(
        conversation_id = conv.id,
        auteur_id       = user.id,
        contenu         = data["contenu"],
    )
    db.session.add(msg)

    # Mettre à jour statut si réponse du garage
    if user.role in ("vendeur", "admin") and conv.statut == "ouvert":
        conv.statut = "en_cours"

    db.session.commit()
    return jsonify(msg.to_dict()), 201


# ── PATCH /api/messages/conversations/<id>/statut ────────────
@bp.patch("/conversations/<int:conv_id>/statut")
@jwt_required()
def update_statut(conv_id):
    user = current_user()
    if user.role not in ("vendeur", "admin"):
        return jsonify({"error": "Accès interdit"}), 403

    conv = Conversation.query.get_or_404(conv_id)
    new_statut = request.get_json().get("statut")
    valid = ("ouvert", "en_cours", "resolu", "ferme")
    if new_statut not in valid:
        return jsonify({"error": f"Statut invalide. Valeurs: {valid}"}), 400

    conv.statut = new_statut
    db.session.commit()
    return jsonify(conv.to_dict()), 200
