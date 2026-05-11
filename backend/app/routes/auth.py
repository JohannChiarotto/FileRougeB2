from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from app import db
from app.models.utilisateur import Utilisateur

bp = Blueprint("auth", __name__)


@bp.post("/register")
def register():
    data = request.get_json()
    required = ("prenom", "nom", "email", "password")
    if not all(data.get(f) for f in required):
        return jsonify({"error": "Champs obligatoires manquants"}), 400

    if Utilisateur.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email déjà utilisé"}), 409

    user = Utilisateur(
        prenom=data["prenom"].strip(),
        nom=data["nom"].strip(),
        email=data["email"].lower().strip(),
        telephone=data.get("telephone"),
        role="client",
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Compte créé avec succès",
        "user": user.to_dict()
    }), 201


@bp.post("/login")
def login():
    data = request.get_json()
    email    = data.get("email", "").lower().strip()
    password = data.get("password", "")

    user = Utilisateur.query.filter_by(email=email, est_actif=True).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Identifiants invalides"}), 401

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "user":          user.to_dict(),
    }), 200


@bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": access_token}), 200


@bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = Utilisateur.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200


@bp.put("/me")
@jwt_required()
def update_me():
    user_id = int(get_jwt_identity())
    user = Utilisateur.query.get_or_404(user_id)
    data = request.get_json()

    for field in ("prenom", "nom", "telephone"):
        if field in data:
            setattr(user, field, data[field])

    if "password" in data and data["password"]:
        user.set_password(data["password"])

    db.session.commit()
    return jsonify(user.to_dict()), 200
