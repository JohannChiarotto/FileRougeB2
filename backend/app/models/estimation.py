from app import db


class DemandeEstimation(db.Model):
    __tablename__ = "demandes_estimations"

    id = db.Column(db.Integer, primary_key=True)
    marque = db.Column(db.String(120), nullable=False)
    modele = db.Column(db.String(120), nullable=False)
    annee = db.Column(db.SmallInteger, nullable=False)
    kilometrage = db.Column(db.Integer, nullable=False, default=0)
    energie = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    statut = db.Column(db.String(20), nullable=False, default="en_attente")
    commentaire_admin = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "marque": self.marque,
            "modele": self.modele,
            "annee": self.annee,
            "kilometrage": self.kilometrage,
            "energie": self.energie,
            "email": self.email,
            "statut": self.statut,
            "commentaire_admin": self.commentaire_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
