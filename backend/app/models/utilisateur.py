import bcrypt
from app import db


class Utilisateur(db.Model):
    __tablename__ = "utilisateurs"

    id            = db.Column(db.Integer, primary_key=True)
    uuid          = db.Column(db.String(36), unique=True, nullable=False,
                              server_default=db.func.uuid_generate_v4())
    prenom        = db.Column(db.String(80),  nullable=False)
    nom           = db.Column(db.String(80),  nullable=False)
    email         = db.Column(db.String(150), nullable=False, unique=True)
    telephone     = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20),  default="client")
    agence_id     = db.Column(db.Integer, db.ForeignKey("agences.id"), nullable=True)
    est_actif     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, server_default=db.func.now())
    updated_at    = db.Column(db.DateTime, server_default=db.func.now())

    conversations = db.relationship("Conversation", back_populates="client",
                                    foreign_keys="Conversation.client_id", lazy="dynamic")
    rdvs          = db.relationship("RendezVous", back_populates="client", lazy="dynamic")

    # ── Mot de passe ─────────────────────────────────────────────

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password_hash.encode("utf-8")
        )

    # ── Sérialisation ─────────────────────────────────────────────

    def to_dict(self, include_private: bool = False):
        data = {
            "id":         self.id,
            "uuid":       self.uuid,
            "prenom":     self.prenom,
            "nom":        self.nom,
            "email":      self.email,
            "telephone":  self.telephone,
            "role":       self.role,
            "agence_id":  self.agence_id,
            "est_actif":  self.est_actif,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        return data

    def __repr__(self):
        return f"<Utilisateur {self.email}>"
