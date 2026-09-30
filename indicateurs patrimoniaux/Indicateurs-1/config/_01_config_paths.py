"""
Centralise tous les chemins (fichiers, dossiers de sortie).
"""
from pathlib import Path
from datetime import datetime
from utils.constants import Paths

# Année courante pour les noms de fichiers dynamiques
current_year = datetime.now().year

# Chemin racine du projet
ROOT_DIR = Path(__file__).parent.parent
SQL_DIR = ROOT_DIR / "SQL"

# Dossier de sortie principal pour les résultats
SORTIE_DIR = ROOT_DIR / "resultats"
SORTIE_DIR.mkdir(parents=True, exist_ok=True)

# Définition des répertoires de données sources
DOSSIER_PAG = Path("L:/EGDD/DAEA/PAG")
DOSSIER_ASSAINISSEMENT = Path("H:/DTEE/EAU")
DOSSIER_OGEP = DOSSIER_ASSAINISSEMENT / "OGEP"
DOSSIER_CARTO = Path(
    "L:/EGDD/DAEA/PAG/E_GDP/Projets transversaux/_Cartographie/__Environnement Cartographique")
DOSSIER_ARCHIVE_CONNEXES = Path(
    f"H:/DTEE/EAU/ARCHIVES SIG/archives {current_year}/Documents_connexes")
DOSSIER_ARCHIVE = Path(f"H:/DTEE/EAU/ARCHIVES SIG")
DOSSIER_ARCHIVE_SOCLE = Path(
    f"H:/DTEE/EAU/ARCHIVES SIG/archives {current_year}/Archives_socle")

mapping_paths_by_year = {
    'live': {
        "PATH_ARCHIVE": {},  # Vide : requetes SQL directes sur la BDD
        "PATH_ARCHIVE_CONNEXES": {
            Paths.CADASTRE: DOSSIER_ARCHIVE_CONNEXES / "Cadastre_archives_2024.gpkg",
            Paths.RECOLEMENT_OUVRAGES: DOSSIER_ARCHIVE_CONNEXES / "Ouvrages_ESU.xlsx",
            Paths.ETAT_SANTE_USINES: DOSSIER_ARCHIVE_CONNEXES / "Patrimoines_Usines_Etat_Sante.xls",
            Paths.IDCAPTURE_CAMPAGNE: DOSSIER_ARCHIVE_CONNEXES / "idcapture-Patrimoines Usines-Campagne.xlsx",
            Paths.REGROUPEMENT_BV: DOSSIER_ARCHIVE_CONNEXES / "BV_REGROUPEMENT.xlsx",
            Paths.RATIO_COUT_PATRIMOINE: DOSSIER_ARCHIVE_CONNEXES / "Ratio cout patrimoine.xlsx",
            Paths.BDD_BASSIN: DOSSIER_ARCHIVE_CONNEXES / "BDD_Bassin.xlsx",
            Paths.INVENTAIRE_OGEP: DOSSIER_ARCHIVE_CONNEXES / "Inventaire_OGEP.xlsx"
        },
        "PATH_DATA_PARTAGES": {
            Paths.AGEC: DOSSIER_CARTO / "_DATA_PARTAGE/Reseaux_AGEC/fevrier2025/portions_avec_etudes_fev2025.shp",
            Paths.ASSCANEXP_ITV: DOSSIER_CARTO / f"14_Observations_ITV_12-2023/DATA/dec_2024/ASSCANEXP_ITV.shp",
            Paths.OVERLAPS_CADASTRE: DOSSIER_CARTO / "4_Etude_domanialite_reseau_emprise_ouvrage/DATA/mars_2025/canexp_overlaps_cadastre.gpkg",
            Paths.OVERLAPS_VOIE: DOSSIER_CARTO / "4_Etude_domanialite_reseau_emprise_ouvrage/DATA/mars_2025/canexp_overlaps_voie.gpkg",
            Paths.IDEES_TRAVAUX: DOSSIER_CARTO / "_DATA_PARTAGE/Reseaux_Idée_tx/2025/couche_idf.dbf",
        }
    },

 '2026': {
    "PATH_ARCHIVE": {
        Paths.ASSAINISSEMENT: DOSSIER_ARCHIVE_SOCLE / "Assainissement_archives_2025.gpkg",
        Paths.EAUPOTABLE: DOSSIER_ARCHIVE_SOCLE / "Eaupotable_archives_2025.gpkg",
        Paths.EAUGENERAL: DOSSIER_ARCHIVE_SOCLE / "Eaugeneral_archives_2025.gpkg",
        Paths.MILIEUAQUATIQUE: DOSSIER_ARCHIVE_SOCLE / "Milieuxaquatiques_archives_2025.gpkg"
    },
    "PATH_ARCHIVE_CONNEXES": {
        
        Paths.CADASTRE: DOSSIER_ARCHIVE_CONNEXES / "Cadastre_archives_2024.gpkg",
        Paths.RECOLEMENT_OUVRAGES: DOSSIER_ARCHIVE_CONNEXES / "Ouvrages_ESU.xlsx",
        Paths.ETAT_SANTE_USINES: DOSSIER_ARCHIVE_CONNEXES / "Patrimoines_Usines_Etat_Sante.xls",
        Paths.IDCAPTURE_CAMPAGNE: DOSSIER_ARCHIVE_CONNEXES / "idcapture-Patrimoines Usines-Campagne.xlsx",
        Paths.REGROUPEMENT_BV: DOSSIER_ARCHIVE_CONNEXES / "BV_REGROUPEMENT.xlsx",
        Paths.RATIO_COUT_PATRIMOINE: DOSSIER_ARCHIVE_CONNEXES / "Ratio cout patrimoine.xlsx",
        Paths.BDD_BASSIN: DOSSIER_ARCHIVE_CONNEXES / "BDD_Bassin.xlsx",
        Paths.INVENTAIRE_OGEP: DOSSIER_ARCHIVE_CONNEXES / "Inventaire_OGEP.xlsx"
    },
    "PATH_DATA_PARTAGES": {
        
        Paths.AGEC: DOSSIER_CARTO / "_DATA_PARTAGE/Reseaux_AGEC/fevrier2026/portions_avec_etudes_fev2026.shp",
        Paths.ASSCANEXP_ITV: DOSSIER_CARTO / "14_Observations_ITV_12-2023/DATA/dec_2024/ASSCANEXP_ITV.shp",
        Paths.OVERLAPS_CADASTRE: DOSSIER_CARTO / "4_Etude_domanialite_reseau_emprise_ouvrage/DATA/octobre_2025/canexp_overlaps_cadastre.gpkg",
        Paths.OVERLAPS_VOIE: DOSSIER_CARTO / "4_Etude_domanialite_reseau_emprise_ouvrage/DATA/octobre_2025/canexp_overlaps_voie.gpkg",
        Paths.IDEES_TRAVAUX: DOSSIER_CARTO / "_DATA_PARTAGE/Reseaux_Idée_tx/2025/couche_idf.dbf",
    }
},
    '2025': {
        "PATH_ARCHIVE": {
            Paths.ASSAINISSEMENT: DOSSIER_ARCHIVE_SOCLE / "Assainissement_archives_2024.gpkg",
            Paths.EAUPOTABLE: DOSSIER_ARCHIVE_SOCLE / "Eaupotable_archives_2024.gpkg",
            Paths.EAUGENERAL: DOSSIER_ARCHIVE_SOCLE / "Eaugeneral_archives_2024.gpkg",
            Paths.MILIEUAQUATIQUE: DOSSIER_ARCHIVE_SOCLE /
            "Milieuxaquatiques_archives_2024.gpkg"
        },
        "PATH_ARCHIVE_CONNEXES": {
            Paths.CADASTRE: DOSSIER_ARCHIVE_CONNEXES / "Cadastre_archives_2024.gpkg",
            Paths.RECOLEMENT_OUVRAGES: DOSSIER_ARCHIVE_CONNEXES / "Ouvrages_ESU.xlsx",
            Paths.ETAT_SANTE_USINES: DOSSIER_ARCHIVE_CONNEXES / "Patrimoines_Usines_Etat_Sante.xls",
            Paths.IDCAPTURE_CAMPAGNE: DOSSIER_ARCHIVE_CONNEXES / "idcapture-Patrimoines Usines-Campagne.xlsx",
            Paths.REGROUPEMENT_BV: DOSSIER_ARCHIVE_CONNEXES / "BV_REGROUPEMENT.xlsx",
            Paths.RATIO_COUT_PATRIMOINE: DOSSIER_ARCHIVE_CONNEXES / "Ratio cout patrimoine.xlsx",
            Paths.BDD_BASSIN: DOSSIER_ARCHIVE_CONNEXES / "BDD_Bassin.xlsx",
            Paths.INVENTAIRE_OGEP: DOSSIER_ARCHIVE_CONNEXES / "Inventaire_OGEP.xlsx"
        },
        "PATH_DATA_PARTAGES": {
            Paths.AGEC: DOSSIER_CARTO / "_DATA_PARTAGE/Reseaux_AGEC/fevrier2025/portions_avec_etudes_fev2025.shp",
            Paths.ASSCANEXP_ITV: DOSSIER_CARTO / f"14_Observations_ITV_12-2023/DATA/dec_2024/ASSCANEXP_ITV.shp",
            Paths.OVERLAPS_CADASTRE: DOSSIER_CARTO / "4_Etude_domanialite_reseau_emprise_ouvrage/DATA/mars_2025/canexp_overlaps_cadastre.gpkg",
            Paths.OVERLAPS_VOIE: DOSSIER_CARTO / "4_Etude_domanialite_reseau_emprise_ouvrage/DATA/mars_2025/canexp_overlaps_voie.gpkg",
            Paths.IDEES_TRAVAUX: DOSSIER_CARTO / "_DATA_PARTAGE/Reseaux_Idée_tx/2025/couche_idf.dbf",
        }
    },
    '2024': {
        "PATH_ARCHIVE": {
            Paths.ASSAINISSEMENT: DOSSIER_ARCHIVE / f"archives 2024/archives_ASS_2023.gpkg",
            Paths.EAUPOTABLE: DOSSIER_ARCHIVE / f"archives 2024/AEP_Archives_2023.gpkg",
            Paths.EAUGENERAL: DOSSIER_ARCHIVE / f"archives 2024/EAU_Archives_2023.gpkg",
            Paths.MILIEUAQUATIQUE: DOSSIER_ARCHIVE / f"archives 2024/MAQ_Archives_2023.gpkg",
        },
        "PATH_ARCHIVE_CONNEXES": {},
        "PATH_DATA_PARTAGES": {}
    },
    '2023': {
        "PATH_ARCHIVE": {
            Paths.ASSAINISSEMENT: DOSSIER_ARCHIVE / f"archives 2023/ASS_Archives_2022_sans_doublon.gpkg",
            Paths.EAUPOTABLE: DOSSIER_ARCHIVE / f"archives 2023/AEP_Archives_2022.gpkg",
            Paths.EAUGENERAL: DOSSIER_ARCHIVE / f"archives 2023/EAU_Archives_2022.gpkg",
            Paths.MILIEUAQUATIQUE: DOSSIER_ARCHIVE / f"archives 2023/MAQ_Archives_2022.gpkg",
        },
        "PATH_ARCHIVE_CONNEXES": {},
        "PATH_DATA_PARTAGES": {}
    },
    '2022': {
        "PATH_ARCHIVE": {
            Paths.ASSAINISSEMENT: DOSSIER_ARCHIVE / f"archives 2022/geopackage/ASS_Archives_2021.gpkg",
            Paths.EAUPOTABLE: DOSSIER_ARCHIVE / f"archives 2022/geopackage/AEP_Archives_2021.gpkg",
            Paths.EAUGENERAL: DOSSIER_ARCHIVE / f"archives 2022/geopackage/EAU_Archives_2021.gpkg",
            Paths.MILIEUAQUATIQUE: DOSSIER_ARCHIVE / f"archives 2022/geopackage/MAQ_Archives_2021.gpkg",
        },
        "PATH_ARCHIVE_CONNEXES": {},
        "PATH_DATA_PARTAGES": {}
    },
    '2021': {
        "PATH_ARCHIVE": {
            Paths.ASSAINISSEMENT: DOSSIER_ARCHIVE / f"archives 2021/geopackage/ASS_Archives_2020.gpkg",
            Paths.EAUPOTABLE: DOSSIER_ARCHIVE / f"archives 2021/geopackage/AEP_Archives_2020.gpkg",
            Paths.EAUGENERAL: DOSSIER_ARCHIVE / f"archives 2021/geopackage/EAU_Archives_2020.gpkg",
            Paths.MILIEUAQUATIQUE: DOSSIER_ARCHIVE / f"archives 2021/geopackage/MAQ_Archives_2020.gpkg",
        },
        "PATH_ARCHIVE_CONNEXES": {},
        "PATH_DATA_PARTAGES": {}
    },
    '2020': {},  # TODO mais pas de sauvegarde GPKG
    '2019': {},  # TODO mais pas de sauvegarde GPKG
    '2018': {},  # TODO mais pas de sauvegarde GPKG
    '2017': {}   # TODO mais pas de sauvegarde GPKG
}
