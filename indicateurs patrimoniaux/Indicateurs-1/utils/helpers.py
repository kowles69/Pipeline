"""
Fonctions utilitaires (ex: formatage des nombres).
"""
from shapely.wkb import loads as wkb_loads
import os
from datetime import datetime
from utils.constants import Data, Geo
import pandas as pd
import numpy as np


def convert_geometry(geom):
    if isinstance(geom, str):
        return wkb_loads(bytes.fromhex(geom))
    else:
        return geom  # Already a geometry object


def get_group_column(niveau_extraction):
    """Détermine la colonne de groupement en fonction du niveau d'extraction"""
    if niveau_extraction == Geo.COMMUNE:
        return Data.TEXTE
    elif niveau_extraction == Geo.SYS_ASSAINISSEMENT:
        return Data.NOM_STEU
    elif niveau_extraction == Geo.BASSIN_VERSANT:
        return Data.BASSIN
    elif niveau_extraction == Geo.CAPTAGE:
        return Data.NOM_CAPTAGE
    else:  # METROPOLE
        return None


def create_results_directory(base_folder_name):
    """Crée le dossier de résultats s'il n'existe pas"""
    if not os.path.exists('./resultats'):
        os.makedirs('./resultats')

    # Créer un sous-dossier avec timestamp pour le run
    timestamp = datetime.now().strftime("%Y_%m_%d")
    results_dir = f'./resultats/run_{base_folder_name}_{timestamp}'
    os.makedirs(results_dir, exist_ok=True)

    return results_dir


def make_serializable_rounded(obj, decimals=2):
    if isinstance(obj, pd.DataFrame):
        # Créer une copie pour éviter de modifier l'original
        df_copy = obj.copy()

        # Arrondir seulement les colonnes numériques
        numeric_columns = df_copy.select_dtypes(include=[np.number]).columns
        df_copy[numeric_columns] = df_copy[numeric_columns].round(decimals)

        return df_copy.to_dict('records')
    elif isinstance(obj, pd.Series):
        if obj.dtype in ['float64', 'float32', 'int64', 'int32']:
            return obj.round(decimals).to_list()
        return obj.to_list()
    elif isinstance(obj, (int, float, np.integer, np.floating)):
        return round(float(obj), decimals)
    elif isinstance(obj, dict):
        return {key: make_serializable_rounded(value, decimals) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable_rounded(item, decimals) for item in obj]
    else:
        return obj
