from app import db


class RendezVous(db.Model):
    __tablename__ = "rendez_vous"

    id          = db.Column(db.Integer, primary_key=True)
    client_id   = db.Column(db.Integer, db.ForeignKey("utilisateurs.id"), nullable=False)
    agence_id   = db.Column(db.Integer, db.ForeignKey("agences.id"),       nullable=False)
    vehicule_id = db.Column(db.Integer, db.ForeignKey("vehicules.id"))
    type_rdv    = db.Column(db.String(30), nullable=False)
    statut      = db.Column(db.String(20), default="en_attente")
    date_heure  = db.Column(db.DateTime,   nullable=False)
    duree_min   = db.Column(db.SmallInteger, default=60)
    notes       = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, server_default=db.func.now())
    updated_at  = db.Column(db.DateTime, server_default=db.func.now())

    client   = db.relationship("Utilisateur", back_populates="rdvs")
    agence   = db.relationship("Agence",      back_populates="rdvs")
    vehicule = db.relationship("Vehicule")

    def to_dict(self):
        return {
            "id":          self.id,
            "client":      f"{self.client.prenom} {self.client.nom}" if self.client else None,
            "agence":      self.agence.nom if self.agence else None,
            "vehicule":    f"{self.vehicule.marque.nom} {self.vehicule.modele.nom}"
                           if self.vehicule else None,
            "type_rdv":    self.type_rdv,
            "statut":      self.statut,
            "date_heure":  self.date_heure.isoformat() if self.date_heure else None,
            "duree_min":   self.duree_min,
            "notes":       self.notes,
        }
