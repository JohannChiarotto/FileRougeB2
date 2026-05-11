from app import db


class Conversation(db.Model):
    __tablename__ = "conversations"

    id          = db.Column(db.Integer, primary_key=True)
    uuid        = db.Column(db.String(36), unique=True, nullable=False,
                            server_default=db.func.uuid_generate_v4())
    client_id   = db.Column(db.Integer, db.ForeignKey("utilisateurs.id"), nullable=False)
    agence_id   = db.Column(db.Integer, db.ForeignKey("agences.id"))
    vehicule_id = db.Column(db.Integer, db.ForeignKey("vehicules.id"))
    sujet       = db.Column(db.String(40), default="autre")
    titre       = db.Column(db.String(200), nullable=False)
    statut      = db.Column(db.String(20), default="ouvert")
    created_at  = db.Column(db.DateTime, server_default=db.func.now())
    updated_at  = db.Column(db.DateTime, server_default=db.func.now())

    client   = db.relationship("Utilisateur", foreign_keys=[client_id],
                                back_populates="conversations")
    agence   = db.relationship("Agence")
    vehicule = db.relationship("Vehicule")
    messages = db.relationship("Message", back_populates="conversation",
                                cascade="all, delete-orphan",
                                order_by="Message.created_at")

    def to_dict(self, with_messages: bool = False):
        data = {
            "id":          self.id,
            "uuid":        self.uuid,
            "titre":       self.titre,
            "sujet":       self.sujet,
            "statut":      self.statut,
            "agence_id":   self.agence_id,
            "vehicule_id": self.vehicule_id,
            "nb_messages": len(self.messages),
            "created_at":  self.created_at.isoformat() if self.created_at else None,
            "updated_at":  self.updated_at.isoformat() if self.updated_at else None,
        }
        if with_messages:
            data["messages"] = [m.to_dict() for m in self.messages]
        return data


class Message(db.Model):
    __tablename__ = "messages"

    id               = db.Column(db.Integer, primary_key=True)
    conversation_id  = db.Column(db.Integer,
                                  db.ForeignKey("conversations.id"), nullable=False)
    auteur_id        = db.Column(db.Integer,
                                  db.ForeignKey("utilisateurs.id"), nullable=False)
    contenu          = db.Column(db.Text, nullable=False)
    est_lu           = db.Column(db.Boolean, default=False)
    created_at       = db.Column(db.DateTime, server_default=db.func.now())

    conversation = db.relationship("Conversation", back_populates="messages")
    auteur       = db.relationship("Utilisateur")

    def to_dict(self):
        return {
            "id":         self.id,
            "auteur":     f"{self.auteur.prenom} {self.auteur.nom}" if self.auteur else None,
            "role":       self.auteur.role if self.auteur else None,
            "contenu":    self.contenu,
            "est_lu":     self.est_lu,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
