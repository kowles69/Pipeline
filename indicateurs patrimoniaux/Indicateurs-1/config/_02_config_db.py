"""
Centralise les identifiants de la BDD (à charger depuis un .env).
"""
import os
from dotenv import load_dotenv
from utils.constants import DB

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

DB_CONFIG = {
    DB.USER: os.getenv(DB.USER),
    DB.PASSWORD: os.getenv(DB.PASSWORD),
    DB.HOST: os.getenv(DB.HOST),
    DB.PORT: os.getenv(DB.PORT),
    DB.NAME: os.getenv(DB.NAME),
}


def get_db_url():
    """Construit l'URL de connexion à la base de données."""
    return DB.URL_FORMAT.format(
        user=DB_CONFIG[DB.USER],
        password=DB_CONFIG[DB.PASSWORD],
        host=DB_CONFIG[DB.HOST],
        port=DB_CONFIG[DB.PORT],
        name=DB_CONFIG[DB.NAME]
    )
