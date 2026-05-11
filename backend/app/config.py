import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY            = os.getenv("SECRET_KEY", "change-me-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY        = os.getenv("JWT_SECRET_KEY", "jwt-change-me")
    JWT_ACCESS_TOKEN_EXPIRES  = 3600          # 1 heure
    JWT_REFRESH_TOKEN_EXPIRES = 604800        # 7 jours
    UPLOAD_FOLDER         = os.getenv("UPLOAD_FOLDER", "/var/www/darri-bolide/uploads")
    MAX_CONTENT_LENGTH    = 20 * 1024 * 1024  # 20 MB
    ALLOWED_EXTENSIONS    = {"jpg", "jpeg", "png", "webp"}

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://darri_user:darri_pass@localhost:5432/darri_bolide_dev"
    )
    SQLALCHEMY_ECHO = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
    }

config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}
