# Importations générales
from utils.constants import Data, Geo
from utils.mapping import mapping
import geopandas as gpd
import sys
from pathlib import Path
from typing import Dict, List, Any
import logging

# Importations des scripts du projet
# Remonte d'un cran depuis le fichier courant
sys.path.append(str(Path(__file__).parent.parent))

# magic strings a ajouter dans le dossier utils
# Chemins vers les fichiers de données
BASE_PATH = Path("H:/DTEE/EAU/ARCHIVES SIG/archives 2025/Archives_socle")
DOCS_PATH = Path("H:/DTEE/EAU/ARCHIVES SIG/archives 2025/Documents_connexes")

PATHS = {
    "assainissement": BASE_PATH / "Assainissement_archives_2024.gpkg",
    "eau_potable": BASE_PATH / "Eaupotable_archives_2024.gpkg",
    "eau_general": BASE_PATH / "Eaugeneral_archives_2024.gpkg",
    "milieux_aquatiques": BASE_PATH / "Milieuxaquatiques_archives_2024.gpkg",
    "cadastre": DOCS_PATH / "Cadastre_archives_2024.gpkg",
}


def load_layer_as_ref(path: str, layer_name: str, schema_type: str = Data.SCHEMA_TYPE_PUB, keep_unmapped_columns: bool = False) -> gpd.GeoDataFrame:
    """
    Charge une couche géographique, la mappe à un schéma de référence et sélectionne les colonnes.

    Args:
        path (str): Chemin vers le fichier de données (ex: GeoPackage).
        layer_name (str): Nom de la couche à charger.
        schema_type (str): Type de schéma à utiliser pour le mapping (ex: 'pub').
        keep_unmapped_columns (bool): Si True, conserve toutes les colonnes après renommage.

    Returns:
        gpd.GeoDataFrame: Le GeoDataFrame traité.
    """
    gdf = gpd.read_file(path, layer=layer_name)

    if schema_type == Data.SCHEMA_TYPE_PUB:
        layer_type = layer_name.split('.')[-1]

        if layer_type in mapping.pub_ref_mappings:
            config = mapping.pub_ref_mappings[layer_type]['pub_to_ref']

            # 1. Renommer les colonnes mappées
            if 'column_mapping' in config:
                gdf = gdf.rename(columns=config['column_mapping'])

            # 2. Transformer les valeurs
            if 'value_mapping' in config:
                for column, value_map in config['value_mapping'].items():
                    if column in gdf.columns:
                        gdf[column] = gdf[column].map(
                            value_map).fillna(gdf[column])

            # 3. Garder seulement les colonnes mappées + geometry (si keep_unmapped_columns=False)
            if not keep_unmapped_columns:
                # Colonnes à conserver
                mapped_columns = set(config.get('column_mapping', {}).values())
                essential_columns = {'geometry'}  # Toujours garder geometry
                columns_to_keep = mapped_columns | essential_columns

                # Filtrer les colonnes qui existent réellement
                existing_columns_to_keep = [
                    col for col in columns_to_keep if col in gdf.columns]

                gdf = gdf[existing_columns_to_keep]

                logging.info(
                    f"Colonnes conservées: {existing_columns_to_keep}")
    logging.info(
        f"  Chargement et mapping de la couche {layer_type} effectué avec succès.")
    return gdf


def perform_sjoin(left_gdf: gpd.GeoDataFrame, right_gdf: gpd.GeoDataFrame, columns: List[str], how: str = 'left', predicate: str = 'intersects') -> gpd.GeoDataFrame:
    """
    Effectue une jointure spatiale et nettoie la colonne d'index résultante.
    """
    joined_gdf = gpd.sjoin(
        left_gdf, right_gdf[columns], how=how, predicate=predicate)
    return joined_gdf.drop(columns=[Data.INDEX_RIGHT], errors='ignore')


def prepare_captages_prioritaires(captage_gdf: gpd.GeoDataFrame, captageperim_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Prépare le GeoDataFrame des périmètres de captages prioritaires.

    Note: Ce calcul est maintenant sorti de la boucle pour n'être fait qu'une fois. 🚀
    """
    captages_prioritaires = captageperim_gdf[captageperim_gdf['niveau']
                                             == Data.NIVEAU_PERIMETRE]
    captages_prioritaires = captages_prioritaires.merge(
        captage_gdf[[Data.IDENTIFIANT_CAPTAGE, Data.NOM_CAPTAGE]],
        on=Data.IDENTIFIANT_CAPTAGE
    )
    # Définir une priorité pour gérer les doublons
    captages_prioritaires['priority'] = captages_prioritaires[Data.IDENTIFIANT_CAPTAGE].apply(
        lambda x: 2 if x == Data.CAPTAGE_PRIO_ID else 1
    )
    # Trier et dédoublonner pour ne garder que le périmètre pertinent par captage
    return captages_prioritaires.sort_values(by=[Data.IDENTIFIANT_CAPTAGE, 'priority']).drop_duplicates(
        subset=[Data.IDENTIFIANT_CAPTAGE], keep='first'
    )


def process_layer(layer_name: str, main_gdf: gpd.GeoDataFrame, context_gdfs: Dict[str, gpd.GeoDataFrame]) -> gpd.GeoDataFrame:
    """
    Applique une série de jointures spatiales à un GeoDataFrame principal.
    """
    # Sauvegarder la géométrie originale et utiliser les centroïdes pour les jointures
    main_gdf[Data.GEOMETRY] = main_gdf.geometry
    main_gdf = main_gdf.set_geometry(main_gdf.geometry.centroid)

    # Jointures spatiales en utilisant la fonction utilitaire
    # Cas spécial pour STEU
    if layer_name == Data.QUERY_STEU:
        main_gdf = perform_sjoin(main_gdf, context_gdfs['bvgrand'], [
                                 'identifiantbvgrand', 'geometry'])
    else:
        main_gdf = perform_sjoin(main_gdf, context_gdfs['bvgrand'], [
                                 'identifiantbvgrand', 'identifiantsteu', 'nomsteu', 'geometry'])

    main_gdf = perform_sjoin(main_gdf, context_gdfs['commune'], [
                             'id_com', 'texte', 'geometry'])
    main_gdf = perform_sjoin(main_gdf, context_gdfs['ruisseaubv'], [
                             'identifiantcoursdeau', 'identifiantbassinversantruisseau', 'geometry'])
    main_gdf = perform_sjoin(main_gdf, context_gdfs['captages_prioritaires'], [
                             Data.IDENTIFIANT_CAPTAGE, Data.NOM_CAPTAGE, 'geometry'])

    # Restaurer la géométrie originale et renommer
    main_gdf = main_gdf.set_geometry(Data.GEOMETRY).drop(
        columns=[Data.CENTROID], errors='ignore')
    main_gdf = main_gdf.rename_geometry(Data.GEOM)

    return main_gdf


def load_base_data_from_annual_save(paths_config) -> Dict[str, gpd.GeoDataFrame]:
    """
    Fonction principale qui orchestre le chargement et le traitement des données.
    """
    layers_config = {
        Data.QUERY_BASSINS: {"path": PATHS["assainissement"], "layer": "pub_assainissement.bassin"},
        "bvgrand": {"path": PATHS["assainissement"], "layer": "pub_assainissement.bvgrand"},
        Data.QUERY_CANAEXP: {"path": PATHS["assainissement"], "layer": "pub_assainissement.canaexp"},
        Data.QUERY_CANAP: {"path": PATHS["assainissement"], "layer": "pub_assainissement.canap"},
        Data.QUERY_CANAS: {"path": PATHS["assainissement"], "layer": "pub_assainissement.canas"},
        Data.QUERY_DO: {"path": PATHS["assainissement"], "layer": "pub_assainissement.devorage"},
        Data.QUERY_DRAIN: {"path": PATHS["assainissement"], "layer": "pub_assainissement.drain"},
        Data.QUERY_OGEP: {"path": PATHS["assainissement"], "layer": "pub_assainissement.ogep"},
        "planrecol": {"path": PATHS["assainissement"], "layer": "pub_assainissement.planrecol"},
        Data.QUERY_PUITS: {"path": PATHS["assainissement"], "layer": "pub_assainissement.puitsf"},
        Data.QUERY_STARE: {"path": PATHS["assainissement"], "layer": "pub_assainissement.stare"},
        Data.QUERY_STEU: {"path": PATHS["assainissement"], "layer": "pub_assainissement.steu"},
        Data.QUERY_TRAITEMENT: {"path": PATHS["assainissement"], "layer": "pub_assainissement.traitement"},
        Data.QUERY_TREMIE: {"path": PATHS["assainissement"], "layer": "pub_assainissement.tremie"},
        Data.QUERY_RESEAU_SEC: {"path": PATHS["eau_general"], "layer": "pub_eaugeneral.reseausec"},
        Data.QUERY_PARCELLES: {
            "path": PATHS["cadastre"], "layer": "parcelleajour"}
    }
    # Chargement de toutes les données initiales
    data = {
        layer: load_layer_as_ref(
            config['path'],
            config['layer'],
            keep_unmapped_columns=True
        )
        for layer, config in layers_config.items()
    }

    # Chargement des données de contexte supplémentaires
    data["commune"] = gpd.read_file(PATHS["cadastre"], layer="commune")
    data["captage"] = gpd.read_file(
        PATHS["eau_potable"], layer="pub_eaupotable.captage")
    data["captageperim"] = gpd.read_file(
        PATHS["eau_potable"], layer="pub_eaupotable.captageperim")
    data["ruisseaubv"] = gpd.read_file(
        PATHS["milieux_aquatiques"], layer="pub_milieuxaquatiques.ruisseaubv")

    captages_prio_gdf = prepare_captages_prioritaires(
        data['captage'], data['captageperim'])

    context_data = {
        'bvgrand': data['bvgrand'],
        'commune': data['commune'],
        'ruisseaubv': data['ruisseaubv'],
        'captages_prioritaires': captages_prio_gdf
    }

    # Traitement des couches principales
    processed_data = {}
    layers_to_process = [Data.QUERY_BASSINS, Data.QUERY_CANAEXP, Data.QUERY_CANAP, Data.QUERY_CANAS, Data.QUERY_DO, Data.QUERY_OGEP, Data.QUERY_PUITS,
                         Data.QUERY_RESEAU_SEC, Data.QUERY_STARE, Data.QUERY_STEU, Data.QUERY_TREMIE, Data.QUERY_TRAITEMENT, Data.QUERY_PARCELLES, Data.QUERY_DRAIN]

    for layer_name in layers_to_process:
        if layer_name in data:
            layer_gdf = data[layer_name]
            processed_data[layer_name] = process_layer(
                layer_name, layer_gdf, context_data)

    # Traitement final spécifique
    if Data.QUERY_TRAITEMENT in processed_data and Data.QUERY_CANAP in processed_data:
        traitement_gdf = processed_data[Data.QUERY_TRAITEMENT]
        canap_gdf = processed_data[Data.QUERY_CANAP]

        processed_data[Data.QUERY_TRAITEMENT] = perform_sjoin(
            traitement_gdf,
            canap_gdf,
            ['identifiantcanap', 'typeadministratifreseau', 'geom'],
            how='inner'
        )
        processed_data[Data.QUERY_TRAITEMENT][Data.RECOLEMENT] = None

    return processed_data
