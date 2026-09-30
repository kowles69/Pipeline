"""
Contient la logique de traitement et nettoyage des données (Pandas/GeoPandas). 
"""
import os
import pandas as pd
import geopandas as gpd
# from config._01_config_paths import PATHS_CONFIG
from datetime import datetime
from utils.helpers import convert_geometry
from utils.constants import Geo, Data, Paths
from data import _01_loader as loader
import pickle
import logging


def load_base_data(save_state, results_dir):
    """Charge les données de base une seule fois pour le batch"""
    base_data_file = os.path.join(results_dir, 'base_data.pkl')

    if not save_state:
        logging.info("\n====== CHARGEMENT DES DONNÉES DE BASE ======")

        # 1. Charger les requêtes SQL
        logging.info("📋 Chargement des requêtes SQL")
        queries = loader.get_sql_queries()
        logging.info(" ✅")

        # 2. Charger les données de la base de données
        logging.info("📋 Chargement des données de la base de données")
        raw_db_data = loader.load_all_data(queries)
        logging.info("✅ Données de la base de donnée chargées")

        # Sauvegarder les données de base
        base_data = {
            'queries': queries,
            'raw_db_data': raw_db_data
        }

        with open(base_data_file, 'wb') as f:
            pickle.dump(base_data, f)
        logging.info(f"💾 Données de base sauvegardées dans: {base_data_file}")

    else:
        # Charger les données de base précédentes
        if os.path.exists(base_data_file):
            logging.info("📂 Chargement des données de base précédentes")
            with open(base_data_file, 'rb') as f:
                base_data = pickle.load(f)
            logging.info(
                f"✅ Données de base chargées depuis: {base_data_file}")
        else:
            logging.info(
                f"❌ Fichier de données de base non trouvé: {base_data_file}")
            logging.info("🔄 Rechargement des données")
            return load_base_data(False, results_dir)

    return base_data['raw_db_data']

 #############################################################################
# FILTRAGE INITIAL DES DONNÉES BRUTES
# ############################################################################


def _filter_by_network_type(data_frames, type_reseau):
    """
    Filtre les données brutes de la BDD en fonction du type de réseau.
    Les conditions de filtrage sont complexes et méritent d'être clarifiées
    pour faciliter la maintenance. TODO
    """
    filtered_dfs = {}

    for key, df in data_frames.items():
        if key == Data.QUERY_CANAEXP:
            is_metropole = df[Data.DOMANIALIT] == Data.METROPOLE_VAL  # M
            if type_reseau == Geo.EU_U:
                is_eu_u_network = (df[Data.TYP_RESEAU] == Data.EAUX_USEES) | (
                    df[Data.TYP_RESEAU] == Data.UNITAIRE)  # A OR B
                is_special_case = (df[Data.TYP_RESEAU] == Data.N_ACCEPTE_PAS_RACCORDEMENT) & (
                    df[Data.TYP_EFFLUEN] != Data.EAUX_PLUVIALES)  # C AND NOT D
                # (A OR B OR (C AND NOT D)) AND M
                filtered_dfs[key] = df[(
                    is_eu_u_network | is_special_case) & is_metropole]
            else:  # EP
                is_ep_network = df[Data.TYP_RESEAU] == Data.EAUX_PLUVIALES
                is_special_case_ep = (df[Data.TYP_RESEAU] == Data.N_ACCEPTE_PAS_RACCORDEMENT) & (
                    df[Data.TYP_EFFLUEN] == Data.EAUX_PLUVIALES)
                filtered_dfs[key] = df[(
                    is_ep_network | is_special_case_ep) & is_metropole]

        elif key == Data.QUERY_CANAP:
            is_domanialite = df[Data.DOMANIALITE] == 2
            if type_reseau == Geo.EU_U:
                is_eu_un = df[Data.TYPE_ADMIN_RESEAU].isin([Geo.EU, Geo.UN])
                is_no_special = (df[Data.TYPE_ADMIN_RESEAU] == Geo.NO) & (
                    df[Data.TYPE_EFFLUENT].isin([Geo.UN, Geo.EU]))
                filtered_dfs[key] = df[(
                    is_eu_un | is_no_special) & is_domanialite]
            else:  # EP
                is_ep = df[Data.TYPE_ADMIN_RESEAU] == Geo.EP
                is_no_ep_special = (df[Data.TYPE_ADMIN_RESEAU] == Geo.NO) & (
                    df[Data.TYPE_EFFLUENT] == Geo.EP)
                filtered_dfs[key] = df[(
                    is_ep | is_no_ep_special) & is_domanialite]

        elif key == Data.QUERY_CANAS:
            if type_reseau == Geo.EU_U:
                filtered_dfs[key] = df[df[Data.TYPE_RESEAU].isin(
                    [Geo.EU, Geo.UN])]
            else:  # EP
                filtered_dfs[key] = df[df[Data.TYPE_RESEAU] == type_reseau]

        elif key == Data.QUERY_TRAITEMENT:
            if type_reseau == Geo.EU_U:
                filtered_dfs[key] = df[df[Data.TYPE_ADMIN_RESEAU].isin(
                    [Geo.EU, Geo.UN])]
            else:  # EP
                filtered_dfs[key] = df[df[Data.TYPE_ADMIN_RESEAU] == Geo.EP]
        else:
            filtered_dfs[key] = df.copy()

    return filtered_dfs


def _process_bassin_versant(data_frames, paths_config):
    """Traite et fusionne les données de regroupement des bassins versants."""
    bvregrp = pd.read_excel(
        paths_config["PATH_ARCHIVE_CONNEXES"][Paths.REGROUPEMENT_BV], sheet_name=Data.SHEET_REGROUPEMENT_BV)
    bvregrp = bvregrp.rename(columns={
                             'identifiant_bassin': Data.ID_BV_RUISSEAU, '2e regroupement': 'identifiant_bassin'})
    bvregrp = bvregrp[[Data.ID_BV_RUISSEAU, 'identifiant_bassin', Data.BASSIN]]

    def concatenate_bassins(group):
        return ', '.join(group.unique())

    bvregrp[Data.BASSIN] = bvregrp.groupby('identifiant_bassin')[
        Data.BASSIN].transform(concatenate_bassins)
    bvregrp.loc[bvregrp[Data.BASSIN] == 'RHONE, RHONE', Data.BASSIN] = 'RHONE'
    bvregrp = bvregrp.drop_duplicates()

    processed_dfs = {}
    for key, df in data_frames.items():
        if Data.ID_BV_RUISSEAU in df.columns:
            processed_dfs[key] = pd.merge(
                df, bvregrp, on=Data.ID_BV_RUISSEAU, how='left')
        else:
            processed_dfs[key] = df
    return processed_dfs

# #############################################################################
# CHARGEMENT DES DONNÉES EXTERNES
# #############################################################################


def load_and_prepare_external_data(type_reseau, paths_config):
    """Charge et prépare les données externes (fichiers Excel, Shapefiles)."""
    external_data = {}
    current_year = datetime.now().year
    date_debut = datetime(current_year-1, 1, 1)
    date_fin = datetime(current_year-1, 12, 31)

    # AGEC data
    logging.info("        Données AGEC")
    gdf_agec = gpd.read_file(paths_config["PATH_DATA_PARTAGES"][Paths.AGEC])
    if type_reseau == Geo.EU_U:
        filtered_gdf_agec = gdf_agec[(gdf_agec["FH_4"] == Geo.EU) | (
            gdf_agec["FH_4"] == Geo.UN)]
    else:
        filtered_gdf_agec = gdf_agec[(gdf_agec["FH_4"] == Geo.EP)]
    filtered_gdf_agec = filtered_gdf_agec.rename(
        columns={'IID_IDENTC': Data.ID_CANAP})
    external_data['gdf_agec'] = filtered_gdf_agec

    # ASSCANEXP_ITV data
    logging.info("        Données d'Inspections Télévisées")
    gdf_itv = gpd.read_file(
        paths_config["PATH_DATA_PARTAGES"][Paths.ASSCANEXP_ITV])
    gdf_itv['ABF'] = pd.to_datetime(
        gdf_itv['ABF'], format='%Y-%m-%d', errors='coerce')
    gdf_itv_year = gdf_itv[(gdf_itv['ABF'] >= date_debut)
                           & (gdf_itv['ABF'] <= date_fin)].copy()
    external_data[Data.VALEURS_UNIQUES_ITV] = gdf_itv['IID_IDENTC'].unique()
    external_data[Data.VALEURS_UNIQUES_ANNUELLES_ITV] = gdf_itv_year['IID_IDENTC'].unique()

    # Etat de santé (IDCapture)
    logging.info("        Données d'état de santé des usines")
    df_etat = pd.read_excel(
        paths_config["PATH_ARCHIVE_CONNEXES"][Paths.ETAT_SANTE_USINES])

    campagne_col = Data.CAMPAGNE_FORMAT.format(current_year - 1)

    if campagne_col not in df_etat.columns:
        logging.warning(f"⚠️ Colonne '{campagne_col}' absente du fichier. Retour de tableaux vides.")
        empty_df = pd.DataFrame(columns=['N°', campagne_col])
        external_data['df_str_etat'] = empty_df.copy()
        external_data['df_steu_etat'] = empty_df.copy()
        external_data['df_tremies_etat'] = pd.DataFrame(columns=[Data.NUMERO, campagne_col])
    else:
        external_data['df_str_etat'] = df_etat[df_etat[Data.TYPE_DE_STATION] == Data.STR].copy()
        external_data['df_steu_etat'] = df_etat[(df_etat[Data.TYPE_DE_STATION] == Data.STEU) | (
            df_etat[Data.TYPE_DE_STATION] == Data.STEP)].copy()
        external_data['df_tremies_etat'] = df_etat[df_etat[Data.TYPE_DE_STATION] == Data.TREMIES].copy()

        external_data['df_str_etat']['N°'] = external_data['df_str_etat'][Data.N_NOM_STATION].str.split(
        ).str[0].str.split('_').str[0]
        external_data['df_str_etat'] = external_data['df_str_etat'][['N°', campagne_col]]

        external_data['df_steu_etat']['N°'] = external_data['df_steu_etat'][Data.N_NOM_STATION].str.split().str[0]
        external_data['df_steu_etat'] = external_data['df_steu_etat'][['N°', campagne_col]]

        external_data['df_tremies_etat'][Data.NUMERO] = external_data['df_tremies_etat'][Data.N_NOM_STATION].str.split().str[0]
        external_data['df_tremies_etat'] = external_data['df_tremies_etat'][[Data.NUMERO, campagne_col]]

    # Nombre d'inspection (IDCapture)
    logging.info("        Nombre d'inspections des usines")
    ins = pd.read_excel(
        paths_config["PATH_ARCHIVE_CONNEXES"][Paths.IDCAPTURE_CAMPAGNE], skiprows=1)
    external_data[Data.INS_STR] = ins[ins[Data.TYPE_DE_STATION]
                                      == Data.STR].copy()
    external_data[Data.INS_STEU] = ins[ins[Data.TYPE_DE_STATION]
                                       == Data.STEP].copy()
    external_data[Data.INS_STR]['N°'] = external_data[Data.INS_STR]['N° - Nom Station'].str.split(
        # Récupérer tous les chiffres avant le premier espace
    ).str[0].str.split('_').str[0]
    external_data[Data.INS_STR]['N°'] = external_data[Data.INS_STR]['N° - Nom Station'].str.split().str[0]
    external_data['ins_tremies'] = ins[ins[Data.TYPE_DE_STATION]
                                       == Data.TREMIES].copy()

    # Linéaire de réseaux sur parcelles ou voies privées
    logging.info("        Linéaires de réseaux sur parcelles ou voies privées")
    external_data[Data.GDF_CAD_OVERLAPS] = gpd.read_file(
        paths_config["PATH_DATA_PARTAGES"][Paths.OVERLAPS_CADASTRE])
    external_data[Data.GDF_CAD_OVERLAPS] = external_data[Data.GDF_CAD_OVERLAPS].rename(
        columns={Data.IID_IDENTCANAEXP: Data.ID_CANA_EXP})
    external_data['gdf_voie_overlaps'] = gpd.read_file(
        paths_config["PATH_DATA_PARTAGES"][Paths.OVERLAPS_VOIE])
    external_data['gdf_voie_overlaps'] = external_data['gdf_voie_overlaps'].rename(
        columns={Data.IID_IDENTCANAEXP: Data.ID_CANA_EXP})

    # Récolement des bassins
    logging.info("        Récolement des bassins")
    external_data['df_recolement_bassins'] = pd.read_excel(
        paths_config["PATH_ARCHIVE_CONNEXES"][Paths.BDD_BASSIN], sheet_name=Data.SHEET_BDD)
    Liste_columns = ['Identifiant', 'Nom ', 'Recolement']
    external_data['df_recolement_bassins'] = external_data['df_recolement_bassins'][Liste_columns]
    external_data['df_recolement_bassins'].columns = [
        'identifiantbassin', 'nombassin', 'Recolement']

    # Récolement des STR et Trémies
    logging.info("        Récolement des STR et Trémies")
    df_recolement_ouvrages = pd.read_excel(
        paths_config["PATH_ARCHIVE_CONNEXES"][Paths.RECOLEMENT_OUVRAGES], sheet_name=None, header=1)
    external_data[Data.DF_RECOLEMENT_STR] = df_recolement_ouvrages[Data.SHEET_STR].copy()
    external_data[Data.DF_RECOLEMENT_TREMIES] = df_recolement_ouvrages[Data.SHEET_TREMIE].copy()
    Liste_columns = [Data.IDENTIFIANT, Data.RECOLE_ON]
    external_data[Data.DF_RECOLEMENT_TREMIES] = external_data[Data.DF_RECOLEMENT_TREMIES][Liste_columns]
    external_data[Data.DF_RECOLEMENT_TREMIES].columns = [
        Data.ID_TREMIE, Data.RECOLEMENT]

    # Récolement des Arbres de Pluie
    logging.info("        Récolement des Arbres de Pluie")
    external_data[Data.DF_RECOLEMENT_AP] = pd.read_excel(
        paths_config["PATH_ARCHIVE_CONNEXES"][Paths.INVENTAIRE_OGEP], sheet_name=Data.SHEET_INV_OUV_DATAGL)
    Liste_columns = ['Identifiant', 'Ouvrage récolé', 'Ouvrage']
    external_data[Data.DF_RECOLEMENT_AP] = external_data[Data.DF_RECOLEMENT_AP][Liste_columns]
    external_data[Data.DF_RECOLEMENT_AP].columns = [
        Data.ID_OGEP, 'Ouvrage récolé', 'Ouvrage']

    # Idées de travaux réseaux
    logging.info("        Idées de travaux réseaux")
    external_data[Data.DF_IDEES_TRAVAUX] = gpd.read_file(
        paths_config["PATH_DATA_PARTAGES"][Paths.IDEES_TRAVAUX])

    # Ratio coût patrimoine
    logging.info("        Ratio coût patrimoine")
    external_data[Data.DF_RATIO_COUT] = pd.read_excel(
        paths_config["PATH_ARCHIVE_CONNEXES"][Paths.RATIO_COUT_PATRIMOINE], sheet_name=Data.SHEET_FEUIL1, header=4)

    return external_data


def process_all_data(raw_db_data, user_options, paths_config):
    """
    Orchestre tout le traitement des données.
    1. Filtre par type de réseau.
    2. Traite les regroupements de bassins versants.
    3. Filtre par zone géographique.
    4. Charge et intègre les données externes.
    """
    type_reseau = user_options['type_reseau']

    # 1. Filtrer par type de réseau
    logging.info("    Filtrage des données par type de réseau.")
    data = _filter_by_network_type(raw_db_data, type_reseau)

    # 2. Traiter les regroupements de bassins versants
    logging.info("    Traitement des regroupements de bassins versants.")
    data = _process_bassin_versant(data, paths_config)

    # 3. Remplir les données manquantes pour les STEUs hors territoire
    logging.info(
        "    Remplissage les données manquantes pour les STEUs hors territoire.")
    if Data.QUERY_STEU in data:
        df_steu = data[Data.QUERY_STEU]
        conditions = (df_steu[Data.NOM_STEU].isin(
            [Data.LISSIEU_1, Data.LISSIEU_2]))
        condition1 = df_steu[Data.NOM_STEU] == Data.LISSIEU_1
        condition2 = df_steu[Data.NOM_STEU] == Data.LISSIEU_2
        df_steu.loc[conditions, Data.TEXTE] = Data.LISSIEU
        df_steu.loc[conditions, Data.ID_COM] = 69117
        df_steu.loc[condition1, Data.ID_BV_GRAND] = Data.LB_LIB
        df_steu.loc[condition1, Data.ID_STEU] = 11
        df_steu.loc[condition2, Data.ID_BV_GRAND] = Data.LS_LIS
        df_steu.loc[condition2, Data.ID_STEU] = 12
        data[Data.QUERY_STEU] = df_steu

    # 5. Charger et préparer les données externes
    logging.info("    Chargement et préparation des données externes.")
    external_data = load_and_prepare_external_data(type_reseau, paths_config)
    data.update(external_data)

    # 6. Traitement spécifique pour les réseaux secs (gdf_glob_EP, gdf_glob_EU_U)
    logging.info("    Traitement des réseaux secs.")
    df_RS = data[Data.QUERY_RESEAU_SEC][data[Data.QUERY_RESEAU_SEC]
                                        ['installation'].isin(['VANN', 'METR'])].copy()
    df_RS[Data.GEOMETRY] = df_RS[Data.GEOM].apply(convert_geometry)
    gdf_RS = gpd.GeoDataFrame(df_RS, geometry=Data.GEOMETRY, crs='EPSG:3946')

    df_RS1 = data[Data.QUERY_CANAP].copy()
    df_RS1[Data.GEOMETRY] = df_RS1[Data.GEOM].apply(convert_geometry)
    gdf_RS1 = gpd.GeoDataFrame(df_RS1, geometry=Data.GEOMETRY, crs='EPSG:3946')

    spatial_join = gpd.sjoin_nearest(
        gdf_RS, gdf_RS1,  how="left", max_distance=10)
    spatial_join[Data.GEOMETRY] = spatial_join['geom_left'].apply(
        convert_geometry)
    gdf_spatial_join = gpd.GeoDataFrame(
        spatial_join, geometry=Data.GEOMETRY, crs='EPSG:3946')
    gdf_spatial_join.rename(columns={'geom_left': Data.GEOM}, inplace=True)

    data[Data.GDF_GLOB_EP] = pd.concat([data[Data.QUERY_RESEAU_SEC][data[Data.QUERY_RESEAU_SEC]['installation']
                                       == 'TREM'], gdf_spatial_join[~gdf_spatial_join[Data.TYPE_ADMIN_RESEAU].isin([Geo.EP])]], ignore_index=True)
    data[Data.GDF_GLOB_EU_U] = pd.concat([data[Data.QUERY_RESEAU_SEC][data[Data.QUERY_RESEAU_SEC]['installation'].isin(
        ['DO', 'STAR'])], gdf_spatial_join[gdf_spatial_join[Data.TYPE_ADMIN_RESEAU].isin([Geo.UN, Geo.EU])]], ignore_index=True)

    data[Data.GDF_GLOB_EP] = data[Data.GDF_GLOB_EP].dropna(subset=[Data.GEOM])
    data[Data.GDF_GLOB_EU_U] = data[Data.GDF_GLOB_EU_U].dropna(subset=[
                                                               Data.GEOM])

    data[Data.GDF_GLOB_EP][Data.GEOMETRY] = data[Data.GDF_GLOB_EP][Data.GEOMETRY].astype(
        'object')
    data[Data.GDF_GLOB_EP]['longueur_troncon'] = data[Data.GDF_GLOB_EP][Data.GEOMETRY].apply(
        lambda x: x.length if hasattr(x, "geom_type") and x.geom_type in ['LineString', 'MultiLineString'] else None)
    data[Data.GDF_GLOB_EU_U][Data.GEOMETRY] = data[Data.GDF_GLOB_EU_U][Data.GEOMETRY].astype(
        'object')
    data[Data.GDF_GLOB_EU_U]['longueur_troncon'] = data[Data.GDF_GLOB_EU_U][Data.GEOMETRY].apply(
        lambda x: x.length if hasattr(x, "geom_type") and x.geom_type in ['LineString', 'MultiLineString'] else None)

    data[Data.GDF_GLOB_EP]['identifiantreseausec'] = data[Data.GDF_GLOB_EP]['identifiantreseausec'].drop_duplicates(
        keep='first')
    data[Data.GDF_GLOB_EU_U]['identifiantreseausec'] = data[Data.GDF_GLOB_EU_U]['identifiantreseausec'].drop_duplicates(
        keep='first')

    data[Data.GDF_GLOB_EU_U] = data[Data.GDF_GLOB_EU_U].drop(columns=['id_com', Data.TEXTE, 'identifiantbvgrand', Data.ID_STEU,
                                                             'geom_right', 'id_com_right', 'identifiantsteu_right', 'identifiantbvgrand_right', 'texte_right'], errors='ignore')
    data[Data.GDF_GLOB_EP] = data[Data.GDF_GLOB_EP].drop(columns=['id_com', Data.TEXTE, 'identifiantbvgrand', Data.ID_STEU,
                                                         'geom_right', 'id_com_right', 'identifiantsteu_right', 'identifiantbvgrand_right', 'texte_right'], errors='ignore')

    nouveaux_noms = {'id_com_left': 'id_com', 'texte_left': Data.TEXTE,
                     'identifiantbvgrand_left': 'identifiantbvgrand', 'identifiantsteu_left': Data.ID_STEU}
    data[Data.GDF_GLOB_EU_U] = data[Data.GDF_GLOB_EU_U].rename(
        columns=nouveaux_noms)
    data[Data.GDF_GLOB_EP] = data[Data.GDF_GLOB_EP].rename(
        columns=nouveaux_noms)
    data[Data.GDF_GLOB_EP] = gpd.GeoDataFrame(data[Data.GDF_GLOB_EP])
    data[Data.GDF_GLOB_EU_U] = gpd.GeoDataFrame(data[Data.GDF_GLOB_EU_U])

    # 7. Traitement pour les linéaires sur parcelles ou voies privées
    logging.info(
        "    Traitement des linéaires sur parcelles ou voies privées.")
    data[Data.CANEXP_CADASTRE_MERGED] = pd.merge(
        data[Data.QUERY_CANAEXP], data[Data.GDF_CAD_OVERLAPS], on=Data.ID_CANA_EXP, how='inner', suffixes=('_canaexp', '_cadastre'))
    data[Data.CANEXP_VOIE_MERGED] = pd.merge(
        data[Data.QUERY_CANAEXP], data['gdf_voie_overlaps'], on=Data.ID_CANA_EXP, how='inner', suffixes=('_canaexp', '_voie'))

    """     # 8. Préparation de gdf_cad pour NPPTR (Nombre de parcelles privées traversées par les réseaux)
    logging.info("    Préparation de gdf_cad pour NPPTR.")
    data['gdf_cad'] = data['13'].copy()
    data['gdf_cad']['geom'] = data['gdf_cad']['geom'].apply(convert_geometry) if isinstance(x, str) else x)
    data['gdf_cad'] = gpd.GeoDataFrame(data['gdf_cad'], geometry='geom', crs='EPSG:3946') """

    # 9. Préparation de df_vis pour LDiagPrediag
    logging.info("    Préparation de df_vis pour LDiagPrediag.")
    data[Data.DF_VIS] = pd.merge(data[Data.QUERY_CANAP][data[Data.QUERY_CANAP]
                                 [Data.HAUTEUR] >= 150], data['gdf_agec'], on=Data.ID_CANAP, how='left')
    type_etat = {Data.CONSERVATOIRE: Data.ETAT_MAUVAIS, Data.CURATIVE: Data.ETAT_DEGRADE,
                 Data.PREVENTIVE: Data.ETAT_CORRECT, Data.SURVEILLANCE: Data.ETAT_BON}
    for key, value in type_etat.items():
        data[Data.DF_VIS].loc[data[Data.DF_VIS]
                              [Data.ET_7] == key, Data.ET_7] = value
    data[Data.DF_VIS][Data.ET_7] = data[Data.DF_VIS][Data.ET_7].fillna(
        Data.PAS_DE_DONNEES)

    # 10. Préparation récolement ST et trémies
    logging.info("    Préparation du récolement des STR et trémies.")
    data[Data.DF_RECOLEMENT_TREMIES] = pd.merge(
        data[Data.DF_RECOLEMENT_TREMIES], data[Data.QUERY_TREMIE], on=Data.ID_TREMIE)
    data[Data.DF_RECOLEMENT_STR] = data[Data.DF_RECOLEMENT_STR].rename(
        columns={"Identifiant": "identifiantstare"})
    data[Data.DF_RECOLEMENT_STR] = pd.merge(
        data[Data.DF_RECOLEMENT_STR], data[Data.QUERY_STARE], on=Data.ID_STARE)

    # 11. Idées travaux réseaux
    logging.info("    Préparation des idées de travaux réseaux.")
    data[Data.DF_IDEES_TRAVAUX] = pd.merge(
        data[Data.DF_IDEES_TRAVAUX], data[Data.QUERY_CANAEXP], on=Data.ID_CANA_EXP)

    # 12. Données liées au récolement des bassins
    data['df_recolement_bassins'] = pd.merge(
        data['df_recolement_bassins'], data[Data.QUERY_BASSINS], on='identifiantbassin')
    data['df_recolement_bassins'] = data['df_recolement_bassins'][(data['df_recolement_bassins']['typebassin'].isin(
        ['BI', 'BR', 'BRI'])) & (data['df_recolement_bassins']['etat'] == 'CON') & (data['df_recolement_bassins']['exploitant'] == 'GLE')]

    # 13. Données Arbres de Pluie
    data[Data.DF_RECOLEMENT_AP] = pd.merge(
        data[Data.DF_RECOLEMENT_AP], data[Data.QUERY_OGEP][data[Data.QUERY_OGEP]['natureogep'] == 7], on='identifiantogep')

    logging.info("    Toutes les données ont été traitées.")

    return data
