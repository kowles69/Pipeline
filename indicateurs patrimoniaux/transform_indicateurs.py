# -*- coding: utf-8 -*-
"""
transform_indicateurs.py
-------------------------
Transforme le fichier JSON produit par la pipeline Python (results_2026.json)
en un CSV au format long (une ligne = une valeur), exploitable directement
comme source de donnees DigDash.

Couvre les 5 niveaux (Metropole, Commune, Systeme Assainissement,
Bassin versant, Captage) x 2 reseaux (EU_U, EP) x tous les indicateurs
presents dans le JSON.

Schema de sortie (colonnes) :
  annee | niveau | type_reseau | entite | indicateur | indicateur_libelle |
  sous_categorie | metrique | metrique_libelle | unite | valeur_num |
  date_extraction

Usage : python3 transform_indicateurs.py results_2026.json indicateurs_long.csv
"""
import csv
import json
import sys
from datetime import date

from libelles import get_indicateur_libelle, get_metrique_libelle, get_unite

ENTITY_FIELDS = ['texte', 'nomsteu', 'Bassin', 'nomcaptage']
LABEL_FIELDS = ['noteindig', 'tranche_age', 'Etat', 'materiau_work', 'Connaissance', 'ET_7']

# Champs techniques du JSON a ne jamais transformer en metrique
# (ex : 'index' = numero de ligne exporte avec l'indicateur NBR hors Metropole)
IGNORED_FIELDS = {'index'}

# Vocabulaire de categories connues (etat de sante, tranches d'age, materiaux,
# connaissance) -> permet de reconnaitre une colonne "large" (une categorie
# par champ, comme au niveau Commune) et de la ramener au meme format long
# que le niveau Metropole (une ligne par categorie).
CATEGORY_VOCAB = {
    'État bon', 'État correct', 'État dégradé', 'État mauvais',
    'Pas de données', 'ITV incomplètes',
    '0-25 ans', '26-50 ans', '51-75 ans', '> 75 ans',
    '0-10 ans', '11-20 ans', '21-30 ans', '> 30 ans',
    'Amiante cimenté', 'Autre', 'Béton armé', 'Béton autre',
    'Maçonnerie', 'Plastique',
    'Connus', 'Estimés', 'Connue', 'Estimée',
}

LEVEL_KEY_MAP = {
    'Metropole': 'Métropole',
    'Commune': 'Commune',
    'Systeme Assainissement': 'Système Assainissement',
    'Bassin versant': 'Bassin Versant',
    'Captage': 'Captage',
}
RESEAU_KEY_MAP = {'EU_U': 'EU_UN', 'EP': 'EP'}

# --- Harmonisation multi-niveau -------------------------------------------
# Constat : pour un meme indicateur, la donnee source utilise des noms de
# metrique DIFFERENTS au niveau Metropole (deja pre-agregee cote pipeline
# amont, un champ "Connaissance"/"Etat"/etc. + 1-2 mesures) et aux 4 autres
# niveaux (une ligne par entite, chaque categorie etalee en colonnes
# "Connus"/"Estimes"/"% Connus"/"Total"/...). Verifie directement sur le
# JSON brut : ce n'est pas un bug de transformation, la structure source
# differe reellement. Consequence sans harmonisation : un widget filtre sur
# le nom de metrique "Metropole" n'affiche rien des lors qu'on change de
# niveau de zoom.
#
# On uniformise donc, pour les indicateurs ci-dessous, le nom de metrique
# des niveaux non-Metropole sur celui utilise par Metropole, pour qu'un
# meme filtre "indicateur + metrique" fonctionne quel que soit le niveau.

# indicateurs a 2 mesures (valeur brute + pourcentage)
HARMONISATION_2_METRIQUES = {
    'ConMat': ('longueur_sum', 'Pourcentage'),
    'CON_MAT': ('longueur_sum', 'Pourcentage'),
    'ConAge': ('longueur_sum', 'Pourcentage'),
    'CON_AGE': ('longueur_sum', 'Pourcentage'),
    'ES_NV': ('longueur_sum', 'Pourcentage'),
    'ES_V': ('longueur_sum', 'Pourcentage'),
    'ES_STEU': ('nbr', 'Pourcentage'),
    'ES_STR': ('nbr', 'Pourcentage'),
}

# indicateurs a 1 seule mesure (juste une valeur brute par sous_categorie)
HARMONISATION_1_METRIQUE = {
    'AR': 'longueur_sum',
    'LRM': 'longueur_sum',
    'AgeSTEU': 'nb_steu',
    'AgeSTR': 'nb_str',
    'AGE_BASSINS': 'nb_bassins',
    'AGE_STR_EP': 'nb_str_ep',
}

# indicateurs ou le JSON source ne fournit AUCUN pourcentage hors Metropole
# (juste des comptages bruts par categorie) -> on le calcule nous-memes,
# pour que le meme widget "Pourcentage" fonctionne aussi a ces niveaux.
INDICATEURS_A_CALCULER_POURCENTAGE = {
    'ES_NV': ('longueur_sum', 'Pourcentage'),
    'ES_V': ('longueur_sum', 'Pourcentage'),
    'ES_STEU': ('nbr', 'Pourcentage'),
    'ES_STR': ('nbr', 'Pourcentage'),
}

# cas particulier : Metropole donne un total unique (nb_total), les autres
# niveaux donnent le detail ouvert/enterre (nb_ENT + nb_OUV) -> on les
# additionne pour reconstituer un nb_total comparable.
HARMONISATION_SOMME = {
    'NBEOT': (['nb_ENT', 'nb_OUV'], 'nb_total'),
}


def harmoniser_multi_niveau(all_rows):
    """Renomme/regroupe les metriques des niveaux non-Metropole pour qu'elles
    correspondent aux noms utilises au niveau Metropole (meme indicateur)."""
    resultat = []
    a_sommer = {}  # (niveau, reseau, entite, indicateur, sous_cat) -> valeur cumulee

    for niveau, reseau, entite, indicateur, sous_cat, metrique, val in all_rows:
        if niveau == 'Métropole':
            resultat.append((niveau, reseau, entite, indicateur, sous_cat, metrique, val))
            continue

        if indicateur in HARMONISATION_SOMME:
            champs, nouveau_nom = HARMONISATION_SOMME[indicateur]
            if metrique in champs:
                cle = (niveau, reseau, entite, indicateur, sous_cat)
                a_sommer[cle] = a_sommer.get(cle, 0) + val
                continue  # rows fusionnees plus bas
            resultat.append((niveau, reseau, entite, indicateur, sous_cat, metrique, val))
            continue

        if indicateur in HARMONISATION_2_METRIQUES:
            metrique_valeur, metrique_pourcentage = HARMONISATION_2_METRIQUES[indicateur]
            if metrique == 'valeur':
                resultat.append((niveau, reseau, entite, indicateur, sous_cat, metrique_valeur, val))
            elif metrique == 'Total' and sous_cat == '':
                pass  # somme redondante, deja recuperable par agregation -> on l'ecarte
            elif isinstance(metrique, str) and metrique.startswith('% '):
                nouvelle_sous_cat = metrique[2:]
                resultat.append((niveau, reseau, entite, indicateur, nouvelle_sous_cat, metrique_pourcentage, val))
            else:
                resultat.append((niveau, reseau, entite, indicateur, sous_cat, metrique, val))
            continue

        if indicateur in HARMONISATION_1_METRIQUE:
            metrique_valeur = HARMONISATION_1_METRIQUE[indicateur]
            if metrique == 'valeur':
                resultat.append((niveau, reseau, entite, indicateur, sous_cat, metrique_valeur, val))
            elif metrique == 'Total' and sous_cat == '':
                pass  # somme redondante
            else:
                resultat.append((niveau, reseau, entite, indicateur, sous_cat, metrique, val))
            continue

        resultat.append((niveau, reseau, entite, indicateur, sous_cat, metrique, val))

    for (niveau, reseau, entite, indicateur, sous_cat), val in a_sommer.items():
        _, nouveau_nom = HARMONISATION_SOMME[indicateur]
        resultat.append((niveau, reseau, entite, indicateur, sous_cat, nouveau_nom, val))

    # Calcul des pourcentages manquants (absents du JSON source hors Metropole)
    totaux = {}  # (niveau, reseau, entite, indicateur) -> somme des sous_categories
    for niveau, reseau, entite, indicateur, sous_cat, metrique, val in resultat:
        if niveau == 'Métropole' or indicateur not in INDICATEURS_A_CALCULER_POURCENTAGE:
            continue
        metrique_valeur, _ = INDICATEURS_A_CALCULER_POURCENTAGE[indicateur]
        if metrique == metrique_valeur and sous_cat:
            cle = (niveau, reseau, entite, indicateur)
            totaux[cle] = totaux.get(cle, 0) + val

    lignes_pourcentage = []
    for niveau, reseau, entite, indicateur, sous_cat, metrique, val in resultat:
        if niveau == 'Métropole' or indicateur not in INDICATEURS_A_CALCULER_POURCENTAGE:
            continue
        metrique_valeur, metrique_pourcentage = INDICATEURS_A_CALCULER_POURCENTAGE[indicateur]
        if metrique == metrique_valeur and sous_cat:
            cle = (niveau, reseau, entite, indicateur)
            total = totaux.get(cle, 0)
            pct = round(val / total * 100, 1) if total else 0
            lignes_pourcentage.append((niveau, reseau, entite, indicateur, sous_cat, metrique_pourcentage, pct))

    return resultat + lignes_pourcentage

ANNEE = 2026
DATE_EXTRACTION = date.today().strftime('%d/%m/%Y')  # format attendu par DigDash (jj/mm/aaaa)


def to_rows(niveau_label, reseau_label, indicateur, items):
    rows = []
    if not isinstance(items, list) or not items:
        return rows

    for item in items:
        # 1. determine entite
        entite = niveau_label if niveau_label == 'Métropole' else None
        entity_field_used = None
        for ef in ENTITY_FIELDS:
            if ef in item:
                entite = item[ef]
                entity_field_used = ef
                break
        if entite is None:
            entite = 'NC'

        # 2. determine sous_categorie via un champ etiquette explicite (niveau Metropole)
        label_field_used = None
        sous_categorie = ''
        for lf in LABEL_FIELDS:
            if lf in item:
                sous_categorie = item[lf]
                label_field_used = lf
                break

        # 3. parcourir les champs restants
        for field, val in item.items():
            if field in (entity_field_used, label_field_used) or field in IGNORED_FIELDS:
                continue
            if not isinstance(val, (int, float)):
                continue  # valeurs texte (ex: 'TODO') ignorees dans le long format numerique

            if label_field_used:
                # deja categorise -> metrique = nom du champ (longueur_sum, Pourcentage, nbr...)
                rows.append((niveau_label, reseau_label, entite, indicateur,
                              sous_categorie, field, val))
            elif field in CATEGORY_VOCAB:
                # format "large" (une colonne par categorie) -> on la ramene en long
                rows.append((niveau_label, reseau_label, entite, indicateur,
                              field, 'valeur', val))
            else:
                # metrique simple, pas de sous-categorie
                rows.append((niveau_label, reseau_label, entite, indicateur,
                              '', field, val))
    return rows


def main(json_path, csv_path):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    all_rows = []
    for raw_key, indicateurs in data.items():
        # raw_key ex: 'Metropole_EU_U', 'Systeme Assainissement_EP'
        for niveau_raw, niveau_label in LEVEL_KEY_MAP.items():
            if raw_key.startswith(niveau_raw + '_'):
                reseau_raw = raw_key[len(niveau_raw) + 1:]
                reseau_label = RESEAU_KEY_MAP.get(reseau_raw, reseau_raw)
                for indicateur, items in indicateurs.items():
                    all_rows.extend(to_rows(niveau_label, reseau_label, indicateur, items))
                break

    all_rows = harmoniser_multi_niveau(all_rows)

    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['annee', 'niveau', 'type_reseau', 'entite', 'indicateur',
                          'indicateur_libelle', 'sous_categorie', 'metrique',
                          'metrique_libelle', 'unite', 'valeur_num', 'date_extraction'])
        for niveau, reseau, entite, indicateur, sous_cat, metrique, val in all_rows:
            writer.writerow([
                ANNEE, niveau, reseau, entite, indicateur,
                get_indicateur_libelle(indicateur),
                sous_cat,
                metrique,
                get_metrique_libelle(indicateur, metrique),
                get_unite(indicateur, metrique),
                val,
                DATE_EXTRACTION,
            ])

    print(f"{len(all_rows)} lignes ecrites dans {csv_path}")
    return len(all_rows)


if __name__ == '__main__':
    json_path = sys.argv[1] if len(sys.argv) > 1 else 'results_2026.json'
    csv_path = sys.argv[2] if len(sys.argv) > 2 else 'indicateurs_long.csv'
    main(json_path, csv_path)
