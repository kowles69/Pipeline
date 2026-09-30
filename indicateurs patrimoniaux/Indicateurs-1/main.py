# Importations générales
from utils.helpers import get_group_column, create_results_directory, make_serializable_rounded
from utils.constants import Geo
from indicators import ep_indicators, eu_u_indicators
from data import _03_loader_archive as processor_archive
from data import _02_processor as processor
from typing import Dict, Any, Tuple
from pathlib import Path
from itertools import product
import pickle
import json
import os
import logging
import warnings
from config._01_config_paths import mapping_paths_by_year
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

#Centralisation de la configuration
NIVEAUX_EXTRACTION = [Geo.METROPOLE, Geo.COMMUNE,
                      Geo.SYS_ASSAINISSEMENT, Geo.BASSIN_VERSANT, Geo.CAPTAGE]
TYPES_RESEAU = [Geo.EP, Geo.EU_U]
INDICATOR_FUNCTIONS = {  # Si d'autres types de réseaux sont ajoutés, les fonctions correspondantes doivent être importées et ajoutées ici
    Geo.EU_U: eu_u_indicators.function,
    Geo.EP: ep_indicators.function
}




def get_data(source: str, use_cache: bool, results_dir: Path, paths_config: Dict[str, Any]) -> Dict[str, Any]:
    """Charge les données soit du socle, soit des archives annuelles.
    TODO : Faire en sorte de pouvoir fonctionner avec SDE"""
    if source == Geo.SOURCE_SOCLE:
        return processor.load_base_data(use_cache, results_dir)
    elif source == Geo.SOURCE_ANNUAL:
        return processor_archive.load_base_data_from_annual_save(paths_config)
    else:
        raise ValueError(
            f"Le paramètre 'source' doit être '{Geo.SOURCE_SOCLE}' ou '{Geo.SOURCE_ANNUAL}'.")


def process_single_combination(options: Dict[str, Any], raw_db_data: Dict[str, Any], use_cache: bool, results_dir: Path, paths_config: Dict[str, Any]) -> Dict[str, Any]:
    """Traite une seule combinaison niveau/réseau avec les données de base déjà chargées"""
    type_reseau = options['type_reseau']
    niveau_extraction = options['niveau_extraction']

    filename_base = f"{niveau_extraction}_{type_reseau}".replace(
        " ", "_").replace("'", "")
    processed_data_file = os.path.join(
        results_dir, f'processed_data_{filename_base}.pkl')

    if use_cache and os.path.exists(processed_data_file):
        logging.info(
            f"📂 Chargement des données traitées depuis le cache : {processed_data_file}")
        with open(processed_data_file, 'rb') as f:
            processed_data = pickle.load(f)
    else:
        logging.info(
            f"⚙️ Traitement des données pour {niveau_extraction} - {type_reseau}")
        processed_data = processor.process_all_data(
            raw_db_data, options, paths_config)
        with open(processed_data_file, 'wb') as f:
            pickle.dump(processed_data, f)
        logging.info(
            f"💾 Données traitées sauvegardées : {processed_data_file}")

    logging.info(
        f"📊 Calcul des indicateurs pour {niveau_extraction} - {type_reseau}")
    group_column = get_group_column(niveau_extraction)
    results = {}

    if type_reseau in INDICATOR_FUNCTIONS:
        results = INDICATOR_FUNCTIONS[type_reseau](
            results, processed_data, group_column)

    # Sauvegarder les résultats
    results_file = os.path.join(results_dir, f'results_{filename_base}.pickle')
    with open(results_file, 'wb') as f:
        pickle.dump(results, f)

    logging.info(f"💾 Résultats sauvegardés: {results_file}")
    logging.info(f"✅ Terminé pour {niveau_extraction} - {type_reseau}")
    return results


def main_process_all(source: str, annee: str, paths_config: Dict[str, Any], use_cache: bool = False) -> Tuple[Dict[str, Any], Path]:
    """Traite toutes les combinaisons possibles de manière optimisée."""
    results_dir = create_results_directory(
        base_folder_name=f"{annee}")
    logging.info(f"📁 Dossier de résultats créé : {results_dir}")

    try:
        raw_db_data = get_data(source, use_cache, results_dir, paths_config)
        logging.info("✅ Données de base prêtes pour tous les traitements")
    except Exception as e:
        logging.error(
            f"❌ Erreur critique lors du chargement des données de base : {e}")
        return None, results_dir

    all_results = {}
    total_combinations = len(NIVEAUX_EXTRACTION) * len(TYPES_RESEAU)

    logging.info(
        f"====== DÉBUT DU TRAITEMENT DES {total_combinations} COMBINAISONS (Année: {annee}) ======")
    for i, (niveau, type_reseau) in enumerate(product(NIVEAUX_EXTRACTION, TYPES_RESEAU), 1):
        logging.info(
            f"🔄 Traitement de la combinaison {i}/{total_combinations} : {niveau} / {type_reseau}")
        options = {'niveau_extraction': niveau, 'type_reseau': type_reseau}
        try:
            results = process_single_combination(
                options, raw_db_data, use_cache, results_dir, paths_config)
            if results is not None:
                all_results[f"{niveau}_{type_reseau}"] = results
        except Exception as e:
            logging.error(
                f"❌ Erreur lors du traitement {niveau} - {type_reseau}: {e}")
            continue

    if not all_results:
        logging.error("❌ Aucun résultat n'a été généré.")
        return None, results_dir

    # Sauvegarde finale de tous les résultats combinés en JSON
    final_json_file = os.path.join(results_dir, f'results_{annee}.json')
    try:
        serializable_results = make_serializable_rounded(
            all_results, decimals=2)
        with open(final_json_file, 'w', encoding='utf-8') as fp:
            json.dump(serializable_results, fp, indent=2, ensure_ascii=False)
        logging.info(
            f"💾 Résultats finaux (JSON) sauvegardés : {final_json_file}")
    except Exception as e:
        logging.error(
            f"❌ Erreur lors de la sauvegarde du fichier JSON final : {e}", exc_info=True)

    logging.info(f"🎉 TRAITEMENT GLOBAL TERMINÉ (Année: {annee})!")
    logging.info(f"📁 Tous les fichiers sont dans : {results_dir}")
    logging.info(
        f"📊 Combinaisons réussies : {len(all_results)}/{total_combinations}")

    return all_results, results_dir


if __name__ == "__main__":
    # --- VOS PARAMÈTRES À CHOISIR ICI ---
    # Mettez l'année que vous voulez traiter (ex: '2024', '2023', ou 'live')
    ANNEE_CHOISIE = '2026'
    # Mettez True pour utiliser le cache, sinon False
    UTILISER_CACHE = False
    # -----------------------------------------

    # Sélectionner la configuration des chemins en fonction de l'année choisie
    selected_paths = mapping_paths_by_year.get(ANNEE_CHOISIE)
    if not selected_paths or (ANNEE_CHOISIE != 'live' and not selected_paths.get("PATH_ARCHIVE")):
        logging.critical(
            f"❌ Configuration des chemins pour l'année '{ANNEE_CHOISIE}' est vide ou invalide. Arrêt.")
        exit()

    # Déterminer la source en fonction de l'année
    source = Geo.SOURCE_SOCLE if ANNEE_CHOISIE == 'live' else Geo.SOURCE_ANNUAL

    logging.info(
        f" Lancement du traitement pour l'année : {ANNEE_CHOISIE} (Source: {source})")

    # Appel de la fonction principale avec les variables définies ci-dessus
    main_process_all(source=source,
                     annee=ANNEE_CHOISIE,
                     paths_config=selected_paths,
                     use_cache=UTILISER_CACHE)
