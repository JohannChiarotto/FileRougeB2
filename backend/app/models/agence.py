from app import db


class Agence(db.Model):
    __tablename__ = "agences"

    id          = db.Column(db.Integer, primary_key=True)
    nom         = db.Column(db.String(100), nullable=False)
    adresse     = db.Column(db.String(255), nullable=False)
    ville       = db.Column(db.String(100), nullable=False)
    code_postal = db.Column(db.String(10),  nullable=False)
    telephone   = db.Column(db.String(20))
    email       = db.Column(db.String(150))
    est_siege   = db.Column(db.Boolean, default=False)
    latitude    = db.Column(db.Numeric(9, 6))
    longitude   = db.Column(db.Numeric(9, 6))
    created_at  = db.Column(db.DateTime, server_default=db.func.now())

    vehicules   = db.relationship("Vehicule", back_populates="agence", lazy="dynamic")
    rdvs        = db.relationship("RendezVous", back_populates="agence", lazy="dynamic")

    def to_dict(self):
        return {
            "id":          self.id,
            "nom":         self.nom,
            "adresse":     self.adresse,
            "ville":       self.ville,
            "code_postal": self.code_postal,
            "telephone":   self.telephone,
            "email":       self.email,
            "est_siege":   self.est_siege,
            "latitude":    float(self.latitude)  if self.latitude  else None,
            "longitude":   float(self.longitude) if self.longitude else None,
        }


class Marque(db.Model):
    __tablename__ = "marques"

    id      = db.Column(db.Integer, primary_key=True)
    nom     = db.Column(db.String(80), nullable=False, unique=True)
    logo    = db.Column(db.String(255))
    modeles = db.relationship("Modele", back_populates="marque", lazy="dynamic")

    def to_dict(self):
        return {"id": self.id, "nom": self.nom, "logo": self.logo}


class Modele(db.Model):
    __tablename__ = "modeles"

    id        = db.Column(db.Integer, primary_key=True)
    marque_id = db.Column(db.Integer, db.ForeignKey("marques.id"), nullable=False)
    nom       = db.Column(db.String(100), nullable=False)
    marque    = db.relationship("Marque", back_populates="modeles")

    def to_dict(self):
        return {"id": self.id, "marque_id": self.marque_id, "nom": self.nom}
