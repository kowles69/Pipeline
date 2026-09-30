"""
Gère la lecture des fichiers SQL et l'exécution des requêtes.
"""
import pandas as pd
from sqlalchemy import create_engine
import concurrent.futures
from config._02_config_db import get_db_url
from config._01_config_paths import SQL_DIR
import os
import logging


def get_sql_queries():
    """Charge toutes les requêtes SQL depuis le dossier SQL."""
    queries = {}
    for filename in sorted(os.listdir(SQL_DIR)):
        if filename.endswith(".sql"):
            with open(SQL_DIR / filename, 'r', encoding='utf-8') as f:
                query_name = os.path.splitext(filename)[0]
                queries[query_name] = f.read()
    return queries


def execute_query(query, engine):
    """Exécute une seule requête SQL."""
    try:
        return pd.read_sql_query(query, engine)
    except Exception as e:
        logging.info(f"Erreur lors de l'exécution de la requête : {e}")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur


def load_all_data(queries):
    """Charge toutes les données depuis la base de données en parallèle."""
    db_url = get_db_url()
    engine = create_engine(db_url)
    data_frames = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_query = {executor.submit(
            execute_query, sql, engine): name for name, sql in queries.items()}
        for future in concurrent.futures.as_completed(future_to_query):
            query_name = future_to_query[future]
            try:
                data_frames[query_name] = future.result()
                logging.info(f"    Requête {query_name} exécutée avec succès.")
            except Exception as exc:
                logging.info(f'    {query_name} a généré une exception: {exc}')

    return data_frames
