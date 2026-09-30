"""
Ce fichier centralise toutes les constantes et les "magic strings" du projet
pour faciliter la maintenance et éviter les erreurs de frappe. 
"""


class Geo:
    # Niveaux d'extraction
    METROPOLE = "Metropole"
    COMMUNE = "Commune"
    SYS_ASSAINISSEMENT = "Systeme Assainissement"
    BASSIN_VERSANT = "Bassin versant"
    CAPTAGE = "Captage"

    # Types de réseau
    EP = "EP"
    EU_U = "EU_U"
    EU = "EU"
    UN = "UN"
    NO = "NO"

    # Sources de données
    SOURCE_SOCLE = 'socle'
    SOURCE_ANNUAL = 'annual'
    SOURCE_SDE = 'sde'  # Pour futur usage TODO


class Paths:
    REGROUPEMENT_BV = "regroupement_bv"
    ASSAINISSEMENT = "assainissement"
    EAUPOTABLE = "eaupotable"
    EAUGENERAL = 'eaugeneral'
    MILIEUAQUATIQUE = "milieuaquatique"
    CADASTRE = "cadastre"
    AGEC = "agec"
    ASSCANEXP_ITV = "asscanexp_itv"
    ETAT_SANTE_USINES = "etat_sante_usines"
    IDCAPTURE_CAMPAGNE = "idcapture_campagne"
    OVERLAPS_CADASTRE = "overlaps_cadastre"
    OVERLAPS_VOIE = "overlaps_voie"
    BDD_BASSIN = "bdd_bassin"
    RECOLEMENT_OUVRAGES = "recolement_ouvrages"
    INVENTAIRE_OGEP = "inventaire_ogep"
    IDEES_TRAVAUX = "idees_travaux"
    RATIO_COUT_PATRIMOINE = "ratio_cout_patrimoine"


class DB:
    USER = 'DB_USER'
    PASSWORD = 'DB_PASSWORD'
    HOST = 'DB_HOST'
    PORT = 'DB_PORT'
    NAME = 'DB_NAME'
    URL_FORMAT = "postgresql://{user}:{password}@{host}:{port}/{name}"


class Data:

    # Clés pour les résultats des requêtes SQL
    QUERY_BASSINS = '0'  # Bassins
    QUERY_CANAEXP = '1'  # Canaexp
    QUERY_CANAP = '2'  # Canap
    QUERY_CANAS = '3'  # Canas
    QUERY_DO = '4'  # Déversoir d'orage
    QUERY_OGEP = '5'  # OGEP
    QUERY_PUITS = '6'  # Puits
    QUERY_RESEAU_SEC = '7'  # Réseau sec
    QUERY_STARE = '8'  # Stare
    QUERY_STEU = '9'  # STEU
    QUERY_TREMIE = '10'  # Trémie
    QUERY_TRAITEMENT = '11'  # Traitement
    QUERY_PARCELLES = '12'  # Parcelles
    QUERY_DRAIN = '13'  # Drains

    # Noms de feuilles Excel
    SHEET_REGROUPEMENT_BV = "Regroupement BV"
    SHEET_BDD = "BDD"
    SHEET_STR = "Str"
    SHEET_TREMIE = "Tremie"
    SHEET_INV_OUV_DATAGL = "INV_OUV_DATAGL"
    SHEET_FEUIL1 = "Feuil1"

    # Noms de colonnes
    TYPE_DE_STATION = 'Type de Station'
    STEP = 'STEP'
    STEU = 'STEU'
    TREMIES = 'TREMIES'
    STR = 'STR'
    N_NOM_STATION = 'N° - Nom Station'
    CAMPAGNE_FORMAT = 'Campagne {}'
    IID_IDENTCANAEXP = 'IID_IDENTCANAEXP'
    IDENTIFIANT = 'Identifiant'
    RECOLE_ON = 'Récolé (O/N)'
    RECOLE_ON_M = 'récolé (O/N)'
    LISSIEU_1 = 'Code 207_Lissieu Le Bourg Le Roty'
    LISSIEU_2 = 'Code 208_Lissieu Dommartin Sémanet'
    LISSIEU = 'LISSIEU'
    ID_COM = 'id_com'
    ID_BV_GRAND = 'identifiantbvgrand'
    LB_LIB = 'LB_LIB'
    LS_LIS = 'LS_LIS'
    MISSING_VALUE = 'MISSING_VALUE'
    OUVRAGE = "Ouvrage"
    ARBRE_DE_PLUIE = "Arbre de pluie"
    GEOMETRY = "geometry"
    GEOM = "geom"
    CENTROID = "centroid"
    INDEX_RIGHT = "index_right"
    IDENTIFIANT_CAPTAGE = "identifiantcaptage"
    NOM_CAPTAGE = "nomcaptage"
    NIVEAU_PERIMETRE = "Eloignée"
    CAPTAGE_PRIO_ID = "E565"
    SCHEMA_TYPE_PUB = "pub"
    GEOM = 'geom'
    GEOMETRY = 'geometry'
    ID_CANA_EXP = 'idcanaexp'
    ID_CANAP = 'identifiantcanap'
    ID_CANAS = 'identifiantcanas'
    ID_PARCELLE = 'idparcelle'
    ID_DEVORAGE = 'identifiantdevorage'
    ID_TRAITEMENT = 'identifianttraitement'
    ID_STARE = 'identifiantstare'
    ID_STEU = 'identifiantsteu'
    ID_TREMIE = 'identifianttremie'
    ID_OGEP = 'identifiantogep'
    ID_PUITSF = 'identifiantpuitsf'
    ID_BASSIN = 'identifiantbassin'
    ID_BV_RUISSEAU = 'identifiantbassinversantruisseau'
    TYPE_RESEAU = 'typereseau'
    TYP_RESEAU = 'typreseau'
    TYP_EFFLUEN = 'typeffluen'
    DOMANIALIT = 'domanialit'
    TYPE_ADMIN_RESEAU = 'typeadministratifreseau'
    TYPE_EFFLUENT = 'typeeffluent'
    DOMANIALITE = 'domanialite'
    TEXTE = 'texte'
    NOM_STEU = 'nomsteu'
    BASSIN = 'Bassin'
    NOM_CAPTAGE = 'nomcaptage'
    MATERIAU = 'materiau'
    MATERIAU_PRESUME = 'materiaupresume'
    ANNEE_POSE = 'anneepose'
    ANNEE_POSE_SUP = 'anneeposesuperieur'
    ANNEE_POSE_INF = 'anneeposeinferieur'
    HAUTEUR = 'hauteur'
    LONGUEUR = 'longueur'
    PRECISION_PLANIMETRIQUE = 'precisionplanimetrique'
    TYPE_TRAITEMENT = 'typetraitement'
    NATURE_OGEP = 'natureogep'
    NATURE = 'nature'
    NUMERO = 'numero'
    ANNEE_CONSTRUCTION = 'anneeconstruction'
    NOTE_INDIG = 'noteindig'
    ET_7 = 'ET_7'
    RECOLEMENT = 'recolement'

    # Valeurs catégorielles
    # Type administratif réseau
    EAUX_USEES = 'Eaux usées'
    UNITAIRE = 'Unitaire'
    EAUX_PLUVIALES = 'Eaux pluviales'
    N_ACCEPTE_PAS_RACCORDEMENT = "N'accepte pas de raccordement"
    METROPOLE_VAL = 'Métropole'
    SAB = 'SAB'
    FAIBLE = 'FAIBLE'
    FORT = 'FORT'
    CLASSE_A = 'A'
    CLASSE_B = 'B'
    CLASSE_C = 'C'
    DIAG = 'DIAG'
    PREDIAG = 'PREDIAG'
    G1, G2, G3, G4, G0 = 'G1', 'G2', 'G3', 'G4', 'G0'
    OUI = 'O'
    NON = 'N'
    CONSERVATOIRE = 'Conservatoire'
    CURATIVE = 'Curative'
    PREVENTIVE = 'Préventive'
    SURVEILLANCE = 'Surveillance'
    PAS_DE_DONNEES = 'Pas de données'

    # Clés de dictionnaire de données
    DF_RATIO_COUT = 'df_ratio_cout'
    GDF_CAD_OVERLAPS = 'gdf_cad_overlaps'
    CANEXP_CADASTRE_MERGED = 'canexp_cadastre_merged'
    CANEXP_VOIE_MERGED = 'canexp_voie_merged'
    DF_RECOLEMENT_STR = 'df_recolement_str'
    DF_IDEES_TRAVAUX = 'df_idees_travaux'
    GDF_GLOB_EU_U = 'gdf_glob_EU_U'
    GDF_GLOB_EP = 'gdf_glob_EP'
    VALEURS_UNIQUES_ITV = 'valeurs_uniques_itv'
    VALEURS_UNIQUES_ANNUELLES_ITV = 'valeurs_uniques_annuelles_itv'
    DF_VIS = 'df_vis'
    INS_STEU = 'ins_steu'
    TOTAL = 'Total'
    REALISE_DANS_L_ANNEE = 'Realise_dans_lannee'
    TOTAL_CUMULE = 'Total_cumule'
    POURCENTAGE_INS = 'Pourcentage_ins'
    DF_RECOLEMENT_AP = 'df_recolement_ap'
    DF_RECOLEMENT_TREMIES = 'df_recolement_tremies'
    DF_TREMIES_ETAT = 'df_tremies_etat'
    INS_STR = 'ins_str'
    DF_STEU_ETAT = 'df_steu_etat'
    DF_DOSSIER_FPR = 'df_dossier_fpr'

    # Tranches d'âge
    AGE_0_10 = '0-10 ans'
    AGE_11_20 = '11-20 ans'
    AGE_21_30 = '21-30 ans'
    AGE_OVER_30 = '> 30 ans'
    AGE_0_25 = '0-25 ans'
    AGE_26_50 = '26-50 ans'
    AGE_51_75 = '51-75 ans'
    AGE_OVER_75 = '> 75 ans'

    # État de santé
    ETAT_MAUVAIS = 'État mauvais'
    ETAT_DEGRADE = 'État dégradé'
    ETAT_CORRECT = 'État correct'
    ETAT_BON = 'État bon'
    ITV_INCOMPLETES = 'ITV incomplètes'


class Indicators:
    # Colonnes de résultats
    LONGUEUR_SUM = 'longueur_sum'
    NOMBRE = 'nombre'
    POURCENTAGE = 'Pourcentage'
    VALEUR = 'Valeur'
    VP_BRANCH = 'VP_branch'
    VP_STR_COL = 'VP_STR'
    VP_STEU_COL = 'VP_STEU'
    VP_FPR_COL = 'VP_FPR'
    VP_TREM_COL = 'VP_TREM'
    VP_AP_COL = 'VAL_AP'
    VP_PI_COL = 'VAL_PI'
    VP_OGEP_COL = 'VP_OGEP'
    VP_OUV = 'VP_OUV'
    VP_ENT = 'VP_ENT'
    VP_TOT = 'VP_tot'
    NBRE_REC = 'nbre_rec'
    NBRE_TOT = 'nbre_tot'
    LONG_IDEE = 'long_idee'
    TOTAL = 'total'
    LONGUEUR_RSEC_FORT = 'longueur_rsec_fort'
    LONGUEUR_RSEC_FAIBLE = 'longueur_rsec_faible'
    POURCENTAGE_FA = 'Pourcentage_FA'
    POURCENTAGE_FO = 'Pourcentage_FO'
    POURCENTAGE_TOT = 'Pourcentage_Tot'
    # Connaissance
    CONNAISSANCE = 'Connaissance'
    CONNUE = 'Connue'
    ESTIMEE = 'Estimée'
    CONNUES = 'Connus'
    ESTIMES = 'Estimés'

    # Types d'ouvrage pour ratio cout
    OUVRAGE_RESEAU_VISITABLE = 'Réseau visitable'
    OUVRAGE_RESEAU_NON_VISITABLE = 'Réseau non visitable'
    OUVRAGE_BRANCHEMENT = 'Branchement'
    OUVRAGE_STEU = 'STEU '
    OUVRAGE_STR_TREMIE = 'STR/trémie '
    OUVRAGE_FPR = 'FPR '
    OUVRAGE_BASSINS_CIEL_OUVERT = "Bassins ciel ouvert "
    OUVRAGE_BASSINS_ENTERRES = 'Bassins enterrés'
    OUVRAGE_LIN_INFILTRATION = "Linéaire d’infiltration (noue, tranchées) "
    OUVRAGE_ARBRES_PLUIE = 'Arbres de pluie'
    OUVRAGE_PUITS_INFILTRATION = 'puits d’infiltration'

    # Autres
    TYPE_OUVRAGE = "Type d'ouvrage"
    RATIO_CHOISI = 'Ratio choisi'
