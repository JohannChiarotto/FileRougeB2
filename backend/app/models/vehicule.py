from app import db


class Vehicule(db.Model):
    __tablename__ = "vehicules"

    id             = db.Column(db.Integer, primary_key=True)
    uuid           = db.Column(db.String(36), unique=True, nullable=False,
                               server_default=db.func.uuid_generate_v4())
    agence_id      = db.Column(db.Integer, db.ForeignKey("agences.id"),  nullable=False)
    marque_id      = db.Column(db.Integer, db.ForeignKey("marques.id"),  nullable=False)
    modele_id      = db.Column(db.Integer, db.ForeignKey("modeles.id"),  nullable=False)
    version        = db.Column(db.String(150))
    annee          = db.Column(db.SmallInteger, nullable=False)
    etat           = db.Column(db.String(20),  nullable=False, default="occasion")
    statut         = db.Column(db.String(20),  nullable=False, default="disponible")
    prix           = db.Column(db.Numeric(10, 2), nullable=False)
    prix_barre     = db.Column(db.Numeric(10, 2))
    kilometrage    = db.Column(db.Integer, default=0)
    energie        = db.Column(db.String(30), nullable=False)
    boite          = db.Column(db.String(20), nullable=False)
    couleur_ext    = db.Column(db.String(60))
    couleur_int    = db.Column(db.String(60))
    nb_portes      = db.Column(db.SmallInteger)
    nb_places      = db.Column(db.SmallInteger)
    puissance_cv   = db.Column(db.SmallInteger)
    puissance_kw   = db.Column(db.SmallInteger)
    cylindree      = db.Column(db.SmallInteger)
    co2            = db.Column(db.SmallInteger)
    consommation   = db.Column(db.Numeric(4, 1))
    vin            = db.Column(db.String(17), unique=True)
    description    = db.Column(db.Text)
    equipements    = db.Column(db.ARRAY(db.String))
    vendeur_id     = db.Column(db.Integer, db.ForeignKey("utilisateurs.id"))
    created_at     = db.Column(db.DateTime, server_default=db.func.now())
    updated_at     = db.Column(db.DateTime, server_default=db.func.now())

    # Relations
    agence  = db.relationship("Agence",  back_populates="vehicules")
    marque  = db.relationship("Marque")
    modele  = db.relationship("Modele")
    vendeur = db.relationship("Utilisateur")
    photos  = db.relationship("PhotoVehicule", back_populates="vehicule",
                               cascade="all, delete-orphan",
                               order_by="PhotoVehicule.ordre")

    def to_dict(self, full: bool = False):
        photo_principale = next(
            (p.url for p in self.photos if p.est_principale), None
        ) or (self.photos[0].url if self.photos else None)

        data = {
            "id":           self.id,
            "uuid":         self.uuid,
            "marque":       self.marque.nom if self.marque else None,
            "modele":       self.modele.nom if self.modele else None,
            "version":      self.version,
            "annee":        self.annee,
            "etat":         self.etat,
            "statut":       self.statut,
            "prix":         float(self.prix),
            "prix_barre":   float(self.prix_barre) if self.prix_barre else None,
            "kilometrage":  self.kilometrage,
            "energie":      self.energie,
            "boite":        self.boite,
            "couleur_ext":  self.couleur_ext,
            "agence":       self.agence.ville if self.agence else None,
            "photo":        photo_principale,
            "created_at":   self.created_at.isoformat() if self.created_at else None,
        }
        if full:
            data.update({
                "couleur_int":   self.couleur_int,
                "nb_portes":     self.nb_portes,
                "nb_places":     self.nb_places,
                "puissance_cv":  self.puissance_cv,
                "puissance_kw":  self.puissance_kw,
                "cylindree":     self.cylindree,
                "co2":           self.co2,
                "consommation":  float(self.consommation) if self.consommation else None,
                "vin":           self.vin,
                "description":   self.description,
                "equipements":   self.equipements or [],
                "photos":        [p.to_dict() for p in self.photos],
                "agence_detail": self.agence.to_dict() if self.agence else None,
            })
        return data


class PhotoVehicule(db.Model):
    __tablename__ = "photos_vehicules"

    id              = db.Column(db.Integer, primary_key=True)
    vehicule_id     = db.Column(db.Integer, db.ForeignKey("vehicules.id"), nullable=False)
    url             = db.Column(db.String(500), nullable=False)
    est_principale  = db.Column(db.Boolean, default=False)
    ordre           = db.Column(db.SmallInteger, default=0)
    created_at      = db.Column(db.DateTime, server_default=db.func.now())

    vehicule = db.relationship("Vehicule", back_populates="photos")

    def to_dict(self):
        return {
            "id":             self.id,
            "url":            self.url,
            "est_principale": self.est_principale,
            "ordre":          self.ordre,
        }
