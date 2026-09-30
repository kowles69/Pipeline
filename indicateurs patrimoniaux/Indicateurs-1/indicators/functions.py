"""
Contient les fonctions de calcul des indicateurs.
Chaque fonction retourne un DataFrame pandas avec les résultats. 
"""
import pandas as pd
import geopandas as gpd
from datetime import datetime
import numpy as np
from utils.helpers import convert_geometry
import os
from utils.constants import Data, Geo, Indicators

# Linéaire de réseaux Unitaire


def LRU(filtered_data, group_column):
    dff = pd.DataFrame()
    df_bis = filtered_data[Data.QUERY_CANAP][(filtered_data[Data.QUERY_CANAP][Data.TYPE_ADMIN_RESEAU] == Geo.UN) | (
        (filtered_data[Data.QUERY_CANAP][Data.TYPE_ADMIN_RESEAU] == Geo.NO) & (filtered_data[Data.QUERY_CANAP][Data.TYPE_EFFLUENT] == Geo.UN))]
    if group_column:
        groupes = df_bis.groupby(group_column)
        indicateur_sum = groupes.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000).astype(int)
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, Indicators.LONGUEUR_SUM]
        dff = pd.DataFrame(resultats)

    else:
        resultats = int(df_bis.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000)
        dff = pd.DataFrame([resultats], columns=[Indicators.LONGUEUR_SUM])
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return (dff)

# Linéaire de réseaux Eaux Usées


def LREU(filtered_data, group_column):
    df_bis = filtered_data[Data.QUERY_CANAP][(filtered_data[Data.QUERY_CANAP][Data.TYPE_ADMIN_RESEAU] == Geo.EU) | (
        (filtered_data[Data.QUERY_CANAP][Data.TYPE_ADMIN_RESEAU] == Geo.NO) & (filtered_data[Data.QUERY_CANAP][Data.TYPE_EFFLUENT] == Geo.EU))]
    if group_column:
        groupes = df_bis.groupby(group_column)
        indicateur_sum = groupes.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000).astype(int)
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, Indicators.LONGUEUR_SUM]
        dff = pd.DataFrame(resultats)

    else:
        resultats = int(df_bis.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000)
        dff = pd.DataFrame([resultats], columns=[Indicators.LONGUEUR_SUM])
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return (dff)

# Linéaire de réseaux


def LEP(filtered_data, group_column):
    if group_column:
        groupes = filtered_data.groupby(group_column)
        indicateur_sum = groupes.apply(lambda x: round(x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000)).astype(int)
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, Indicators.LONGUEUR_SUM]
        dff = pd.DataFrame(resultats)
        if dff.empty:
            dff.loc[0] = [0] * len(dff.columns)
    else:
        resultats_list = [int(filtered_data.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000)]
        dff = pd.DataFrame(resultats_list, columns=[Indicators.LONGUEUR_SUM])
    return (dff)

# Connaissance Matériaux


def ConMat(filtered_data, group_column):
    """
    Calcule le linéaire de réseaux selon la connaissance des matériaux.
    """
    df_ConMat = filtered_data[Data.QUERY_CANAP].copy()

    # Remplir la colonne 'Connaissance'
    df_ConMat[Indicators.CONNAISSANCE] = Data.PAS_DE_DONNEES
    condition1 = df_ConMat[Data.MATERIAU].isnull(
    ) & df_ConMat[Data.MATERIAU_PRESUME].notna()
    condition2 = df_ConMat[Data.MATERIAU].notna()
    df_ConMat.loc[condition1, Indicators.CONNAISSANCE] = Indicators.ESTIMES
    df_ConMat.loc[condition2, Indicators.CONNAISSANCE] = Indicators.CONNUES

    if group_column:
        groupes = df_ConMat.groupby([group_column, Indicators.CONNAISSANCE])
        indicateur_sum = round(groupes.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000))
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column,
                             Indicators.CONNAISSANCE, Indicators.LONGUEUR_SUM]
        dff = pd.DataFrame(resultats)
        dff[Indicators.LONGUEUR_SUM] = dff[Indicators.LONGUEUR_SUM].fillna(
            0).astype(int)

        if dff.empty or sum(dff[Indicators.LONGUEUR_SUM]) == 0:
            dff[Indicators.POURCENTAGE] = 0
        else:
            dff[Indicators.POURCENTAGE] = round(
                (dff[Indicators.LONGUEUR_SUM] * 100) / sum(dff[Indicators.LONGUEUR_SUM]))
    else:
        groupes = df_ConMat.groupby(Indicators.CONNAISSANCE)
        indicateur_sum = round(groupes.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, include_groups=False), 3)
        resultats = indicateur_sum.reset_index()
        resultats.columns = [Indicators.CONNAISSANCE, Indicators.LONGUEUR_SUM]
        dff = pd.DataFrame(resultats)
        if sum(dff[Indicators.LONGUEUR_SUM]) == 0:
            dff[Indicators.POURCENTAGE] = 0
        else:
            dff[Indicators.POURCENTAGE] = round(
                (dff[Indicators.LONGUEUR_SUM] * 100) / sum(dff[Indicators.LONGUEUR_SUM]))

    dff = dff.fillna(0)
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    if group_column:
        # On pivote les données pour que chaque connaissance soit une colonne
        dff_pivot = dff.pivot(
            index=group_column, columns=Indicators.CONNAISSANCE, values=Indicators.LONGUEUR_SUM)
        dff_pivot = dff_pivot.fillna(0).astype(int)

        # Total
        dff_pivot["Total"] = dff_pivot.sum(axis=1)

        # Pourcentages
        for col in [Indicators.CONNUES, Indicators.ESTIMES, Data.PAS_DE_DONNEES]:
            if col not in dff_pivot.columns:
                dff_pivot[col] = 0
            dff_pivot[f"% {col}"] = round(
                (dff_pivot[col] / dff_pivot["Total"]) * 100, 1)

        # On remet le nom de la commune en colonne
        dff = dff_pivot.reset_index()

    return dff


# Linéaire de réseaux par famille de materiau (au global)

def LRM(filtered_data, group_column):
    # Créer une copie des données pour éviter les modifications inattendues
    data = filtered_data[Data.QUERY_CANAP].copy()

    # Étape 1: Récupérer les matériaux de Data.MATERIAU
    data['materiau_work'] = data[Data.MATERIAU].copy()

    # Étape 2: Convertir les valeurs selon le tableau de correspondance
    materiau_mapping = {
        'ACIE': 'AUTR', 'PLOM': 'AUTR', 'AUTR': 'AUTR',
        'BATO': 'BTAM', 'BCAR': 'BTAM', 'BCFA': 'BTAM',
        'BCFN': 'BTAU', 'BIND': 'BTAU', 'BLPB': 'BTAU',
        'FCAL': 'FON', 'FDUC': 'FON', 'FONT': 'FON',
        'PEHD': 'PLAS', 'PETH': 'PLAS', 'PP': 'PLAS', 'PRV': 'PLAS', 'PVCL': 'PLAS',
        'ENDU': 'ROCH', 'GRES': 'ROCH', 'MACO': 'ROCH',
        'AMCI': 'AMCI'
    }

    # Appliquer le mapping pour convertir les matériaux
    data['materiau_work'] = data['materiau_work'].map(materiau_mapping)

    # Étape 3: S'il n'y a pas d'information, compléter avec MATERIAU_PRESUME
    data['materiau_work'] = data['materiau_work'].fillna(
        data[Data.MATERIAU_PRESUME])

    # IMPORTANT: Remplacer les valeurs manquantes AVANT le groupby
    data['materiau_work'] = data['materiau_work'].fillna(Data.MISSING_VALUE)

    if group_column:
        # S'assurer que group_column n'a pas non plus de valeurs manquantes
        data[group_column] = data[group_column].fillna(Data.PAS_DE_DONNEES)

        groupes = data.groupby([group_column, 'materiau_work'], observed=True)
        indicateur_sum = round(groupes.apply(
            lambda x: x.drop_duplicates(subset=Data.ID_CANAP)[
                Data.LONGUEUR].sum()/1000,
            include_groups=False
        ), 3)
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column,
                             'materiau_work', Indicators.LONGUEUR_SUM]

    else:
        groupes = data.groupby('materiau_work', observed=True)
        indicateur_sum = round(groupes.apply(
            lambda x: x.drop_duplicates(subset=Data.ID_CANAP)[
                Data.LONGUEUR].sum()/1000,
            include_groups=False
        ), 3)
        resultats = indicateur_sum.reset_index()
        resultats.columns = ['materiau_work', Indicators.LONGUEUR_SUM]

    dff = resultats.copy()

    # Mapping dictionary avec gestion des valeurs manquantes
    mapping = {
        'AMCI': 'Amiante cimenté',
        'AUTR': 'Autre',
        'BTAM': 'Béton armé',
        'BTAU': 'Béton autre',
        'FONT': 'Fonte',
        'PLAS': 'Plastique',
        'ROCH': 'Maçonnerie',
        Data.MISSING_VALUE: Data.PAS_DE_DONNEES
    }

    # Appliquer le mapping ET gérer les valeurs non mappées
    dff['materiau_work'] = dff['materiau_work'].map(
        mapping).fillna(Data.PAS_DE_DONNEES)

    # Regrouper les lignes avec les mêmes valeurs après mapping (sinon pivot plante)
    if group_column:
        dff = dff.groupby([group_column, 'materiau_work'], as_index=False)[
            Indicators.LONGUEUR_SUM].sum()
    else:
        dff = dff.groupby(['materiau_work'], as_index=False)[
            Indicators.LONGUEUR_SUM].sum()

    if dff.empty:
        # Create proper empty DataFrame structure
        if group_column:
            dff = pd.DataFrame({
                group_column: [Data.PAS_DE_DONNEES],
                'materiau_work': [Data.PAS_DE_DONNEES],
                Indicators.LONGUEUR_SUM: [0]
            })
        else:
            dff = pd.DataFrame({
                'materiau_work': [Data.PAS_DE_DONNEES],
                Indicators.LONGUEUR_SUM: [0]
            })

    # Bloc de transformation pour une ligne par commune
    if group_column:
        dff_pivot = dff.pivot(
            index=group_column, columns='materiau_work', values=Indicators.LONGUEUR_SUM)
        dff_pivot = dff_pivot.fillna(0).round(3)

        # Total
        dff_pivot["Total"] = dff_pivot.sum(axis=1).round(3)

        dff = dff_pivot.reset_index()

    return dff

# Linéaire de réseaux avec matériaux connu


def LRMC(filtered_data, group_column):
    df_bis = filtered_data[Data.QUERY_CANAP][filtered_data[Data.QUERY_CANAP]
                                             [Data.MATERIAU].notna()].copy()
    if group_column:
        df_grouped = df_bis.groupby(group_column)
        df_tot = filtered_data[Data.QUERY_CANAP].groupby(group_column)

        indicateur_sum = df_grouped.apply(lambda x: round(
            x.drop_duplicates(subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 3))
        indicateur_tot = df_tot.apply(lambda x: round(x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 2)).reset_index()

        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, Indicators.LONGUEUR_SUM]
        indicateur_tot.columns = [group_column, 'longueur_tot']
        dff = pd.merge(resultats, indicateur_tot,
                       on=group_column, how='outer').reset_index()
        dff = dff.fillna(0)

        if dff.empty:
            dff[Indicators.POURCENTAGE] = 0
        else:
            dff[Indicators.POURCENTAGE] = (
                dff[Indicators.LONGUEUR_SUM] * 100 / dff['longueur_tot']).astype(int)
    else:
        tot = round(filtered_data[Data.QUERY_CANAP].drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 3)
        resultats = round(df_bis.drop_duplicates(subset=Data.ID_CANAP)[
                          Data.LONGUEUR].sum() / 1000, 3)
        pourcentage = int(resultats * 100 / tot) if tot > 0 else 0
        dff = pd.DataFrame({Indicators.LONGUEUR_SUM: [int(
            resultats)], Indicators.POURCENTAGE: pourcentage})
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff


# Linéaire de réseaux avec matériaux estimé
def LRME(filtered_data, group_column):
    df_bis1 = filtered_data[Data.QUERY_CANAP][~filtered_data[Data.QUERY_CANAP]
                                              [Data.MATERIAU].isnull()]
    df_bis2 = filtered_data[Data.QUERY_CANAP][~filtered_data[Data.QUERY_CANAP]
                                              [Data.MATERIAU_PRESUME].isnull()]

    if group_column:
        groupes1 = df_bis1.groupby(group_column)
        groupes2 = df_bis2.groupby(group_column)
        df_tot = filtered_data[Data.QUERY_CANAP].groupby(group_column)

        indicateur_sum = (groupes2.apply(lambda x: x.drop_duplicates(subset=Data.ID_CANAP)[Data.LONGUEUR].sum(
        )/1000))-(groupes1.apply(lambda x: x.drop_duplicates(subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000))
        indicateur_tot = df_tot.apply(lambda x: round(x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 2)).reset_index()

        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, Indicators.LONGUEUR_SUM]
        indicateur_tot.columns = [group_column, 'longueur_tot']

        dff = pd.merge(resultats, indicateur_tot,
                       on=group_column, how='outer').reset_index()
        dff = dff.fillna(0)

        if dff.empty:
            dff[Indicators.POURCENTAGE] = 0
        else:
            dff[Indicators.POURCENTAGE] = round(
                (dff[Indicators.LONGUEUR_SUM] * 100) / dff['longueur_tot'], 2)
    else:
        resultat1 = round(df_bis1.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 3)
        resultat2 = round(df_bis2.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 3)
        tot = round(filtered_data[Data.QUERY_CANAP].drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 3)
        resultats = round(resultat2 - resultat1, 3)
        pourcentage = round(resultats * 100 / tot, 2) if tot > 0 else 0
        dff = pd.DataFrame(
            {Indicators.LONGUEUR_SUM: [resultats], Indicators.POURCENTAGE: pourcentage})
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Linéaire de réseaux avec matériaux connus et estimes


def LRM_E_C(filtered_data, group_column):
    df_connu = filtered_data[Data.QUERY_CANAP][filtered_data[Data.QUERY_CANAP]
                                               [Data.MATERIAU].notna()]
    df_mat_est = filtered_data[Data.QUERY_CANAP][filtered_data[Data.QUERY_CANAP][Data.MATERIAU].isnull(
    ) & filtered_data[Data.QUERY_CANAP][Data.MATERIAU_PRESUME].notna()]

    if group_column:
        groupes_estimes = df_mat_est.groupby(group_column)
        groupes_connus = df_connu.groupby(group_column)
        df_tot = filtered_data[Data.QUERY_CANAP].groupby(group_column)

        resultats_connus = (round(groupes_connus.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000), 3)).reset_index()
        resultats_estimes = (round(groupes_estimes.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000), 3)).reset_index()
        indicateur_tot = df_tot.apply(lambda x: round(x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 2)).reset_index()

        resultats_estimes.columns = [group_column, 'materiaux_estimes']
        resultats_connus.columns = [group_column, 'materiaux_connus']
        indicateur_tot.columns = [group_column, 'longueur_tot']

        dff = pd.merge(pd.merge(resultats_estimes, resultats_connus, on=group_column,
                       how='outer'), indicateur_tot, on=group_column, how='outer')
        dff = dff.fillna(0)

        if dff.empty:
            dff['Pourcentage_estimes'] = 0
            dff['Pourcentage_connus'] = 0
            dff['Pourcentage_total'] = 0
        else:
            dff['Pourcentage_estimes'] = round(
                (dff['materiaux_estimes'] * 100)/dff['longueur_tot'], 2)
            dff['Pourcentage_connus'] = round(
                (dff['materiaux_connus'] * 100)/dff['longueur_tot'], 2)
            dff['Pourcentage_total'] = 100
    else:
        tot = round(filtered_data[Data.QUERY_CANAP].drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 3)
        resultats1 = round(df_connu.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 3)
        resultats2 = round(df_mat_est.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 3)
        pourcentage1 = round(resultats1 * 100 / tot, 2) if tot > 0 else 0
        pourcentage2 = round(resultats2 * 100 / tot, 2) if tot > 0 else 0
        dff = pd.DataFrame({'materiaux_estimes': [resultats2], 'Pourcentage_estimes': pourcentage2,
                           'materiaux_connus': resultats1, 'Pourcentage_connus': pourcentage1, 'longueur_tot': tot, 'Pourcentage_total': 100})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Linéaire de réseaux visitable (> ou = à 1,5 m) et non visitable (< 150)


def LRV(filtered_data, group_column):
    df_bis1 = filtered_data[filtered_data[Data.HAUTEUR] >= 150].copy()
    df_bis2 = filtered_data[filtered_data[Data.HAUTEUR] < 150].copy()

    if group_column:
        groupes1 = df_bis1.groupby(group_column)
        groupes2 = df_bis2.groupby(group_column)
        df_tot = filtered_data.groupby(group_column)

        indicateur_sum1 = groupes1.apply(lambda x: round(
            x.drop_duplicates(subset=Data.ID_CANAP)[Data.LONGUEUR].sum() / 1000, 3))
        indicateur_sum2 = groupes2.apply(lambda x: round(
            x.drop_duplicates(subset=Data.ID_CANAP)[Data.LONGUEUR].sum() / 1000, 3))
        indicateur_tot = df_tot.apply(lambda x: round(x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum() / 1000, 3)).reset_index()

        resultats1 = indicateur_sum1.reset_index()
        resultats2 = indicateur_sum2.reset_index()
        resultats1.columns = [group_column, 'longueur_visitable']
        resultats2.columns = [group_column, 'longueur_non_visitable']
        indicateur_tot.columns = [group_column, 'longueur_tot']

        dff = pd.merge(pd.merge(resultats1, resultats2, on=group_column,
                       how='outer'), indicateur_tot, on=group_column, how='outer')
        dff = dff.fillna(0)

        if dff.empty:
            dff['Pourcentage_visitable'] = 0
            dff['Pourcentage_non_visitable'] = 0
        else:
            dff['Pourcentage_visitable'] = round(
                (dff['longueur_visitable'] * 100) / dff['longueur_tot'])
            dff['Pourcentage_non_visitable'] = round(
                (dff['longueur_non_visitable'] * 100) / dff['longueur_tot'])
    else:
        tot = round(filtered_data.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum() / 1000, 3)
        resultats1 = round(df_bis1.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum() / 1000, 3)
        resultats2 = round(df_bis2.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum() / 1000, 3)

        pourcentage_vis = round(resultats1 * 100 / tot) if tot > 0 else 0
        pourcentage_non_vis = round(resultats2 * 100 / tot) if tot > 0 else 0
        dff = pd.DataFrame({'longueur_visitable': [resultats1], 'longueur_non_visitable': [
                           resultats2], 'Pourcentage_visitable': [pourcentage_vis], 'Pourcentage_non_visitable': [pourcentage_non_vis]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff
#  connaissance de l'âge des réseaux en classant le linéaire en trois catégories : "Connue" (année de pose renseignée), "Estimée" (fourchette d'années de pose renseignée) et "Pas de données".


def ConAge(filtered_data, group_column):
    """
    Calcule le linéaire de réseaux selon la connaissance de l'année de pose.
    """
    df_ConAnnee = filtered_data[Data.QUERY_CANAP].copy()
    df_ConAnnee[Indicators.CONNAISSANCE] = Data.PAS_DE_DONNEES
    condition1 = (df_ConAnnee[Data.ANNEE_POSE].isnull()) & (
        (df_ConAnnee[Data.ANNEE_POSE_SUP].notna()) | (df_ConAnnee[Data.ANNEE_POSE_INF].notna()))
    condition2 = df_ConAnnee[Data.ANNEE_POSE].notna()
    df_ConAnnee.loc[condition1, Indicators.CONNAISSANCE] = Indicators.ESTIMEE
    df_ConAnnee.loc[condition2, Indicators.CONNAISSANCE] = Indicators.CONNUE

    if group_column:
        groupes = df_ConAnnee.groupby([group_column, Indicators.CONNAISSANCE])
        indicateur_sum = round(groupes.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000))
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column,
                             Indicators.CONNAISSANCE, Indicators.LONGUEUR_SUM]
        dff = pd.DataFrame(resultats)

        total_longueur = sum(dff[Indicators.LONGUEUR_SUM])
        if dff.empty or total_longueur == 0:
            dff[Indicators.POURCENTAGE] = 0
        else:
            dff[Indicators.POURCENTAGE] = round(
                (dff[Indicators.LONGUEUR_SUM] * 100) / total_longueur)
    else:
        groupes = df_ConAnnee.groupby(Indicators.CONNAISSANCE)
        indicateur_sum = round(groupes.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000))
        resultats = indicateur_sum.reset_index()
        resultats.columns = [Indicators.CONNAISSANCE, Indicators.LONGUEUR_SUM]
        dff = pd.DataFrame(resultats)
        total_longueur = sum(dff[Indicators.LONGUEUR_SUM])
        if total_longueur == 0:
            dff[Indicators.POURCENTAGE] = 0
        else:
            dff[Indicators.POURCENTAGE] = round(
                (dff[Indicators.LONGUEUR_SUM] * 100) / total_longueur)

    dff = dff.fillna(0)
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

        # Bloc pour transformer les lignes multiples en une seule ligne par commune
    if group_column:
        # On pivote les données pour que chaque connaissance soit une colonne
        dff_pivot = dff.pivot(
            index=group_column, columns=Indicators.CONNAISSANCE, values=Indicators.LONGUEUR_SUM)
        dff_pivot = dff_pivot.fillna(0).astype(int)

        # Total
        dff_pivot["Total"] = dff_pivot.sum(axis=1)

        # Pourcentages
        for col in [Indicators.CONNUES, Indicators.ESTIMES, Data.PAS_DE_DONNEES]:
            if col not in dff_pivot.columns:
                dff_pivot[col] = 0
            dff_pivot[f"% {col}"] = round(
                (dff_pivot[col] / dff_pivot["Total"]) * 100, 1)

        # On remet le nom de la commune en colonne
        dff = dff_pivot.reset_index()

    return dff

# Nombre de DO


def NDO(filtered_data, group_column):
    if group_column:
        # Liste complète des groupes (ex. toutes les communes)
        all_groups = filtered_data[Data.QUERY_CANAP][group_column].drop_duplicates(
        ).to_frame()

        # Comptage des objets DO
        counts = (filtered_data[Data.QUERY_DO]
                  .groupby(group_column)[Data.ID_DEVORAGE]
                  .nunique()
                  .reset_index())
        counts.columns = [group_column, Indicators.NOMBRE]

        # Left join pour inclure aussi ceux sans DO
        dff = all_groups.merge(counts, on=group_column, how='left').fillna(0)
        dff[Indicators.NOMBRE] = dff[Indicators.NOMBRE].astype(int)

    else:
        total = filtered_data[Data.QUERY_DO][Data.ID_DEVORAGE].nunique()
        dff = pd.DataFrame({Indicators.NOMBRE: [int(total)]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


# Nombre de dessableurs
def NDes(filtered_data, group_column):
    df_bis = filtered_data[Data.QUERY_TRAITEMENT].copy()
    df_bis = df_bis[df_bis[Data.TYPE_TRAITEMENT] == Data.SAB]

    if group_column:
        # liste complète des groupes (communes…)
        all_groups = (
            filtered_data[Data.QUERY_CANAP][group_column]
            .drop_duplicates()
            .to_frame()
        )

        # comptage des traitements SAB par groupe
        counts = (
            df_bis.groupby(group_column)[Data.ID_TRAITEMENT]
                  .nunique()
                  .reset_index(name=Indicators.NOMBRE)
        )

        # garder tous les groupes, mettre 0 si absent
        dff = all_groups.merge(counts, on=group_column, how="left").fillna(0)
        dff[Indicators.NOMBRE] = dff[Indicators.NOMBRE].astype(int)
    else:
        total = int(df_bis[Data.ID_TRAITEMENT].nunique())
        dff = pd.DataFrame({Indicators.NOMBRE: [total]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff


# Nombre de STR
def NSTR(filtered_data, group_column):
    df_NSTR = filtered_data[Data.QUERY_STARE][
        filtered_data[Data.QUERY_STARE][Data.NUMERO].notna() &
        (filtered_data[Data.QUERY_STARE][Data.NUMERO] != 0)
    ]

    if group_column:
        # Liste complète des communes
        toutes_communes = filtered_data[Data.QUERY_CANAP][group_column].drop_duplicates(
        ).to_frame()

        # Comptage des STR
        groupes = df_NSTR.groupby(group_column)[
            Data.ID_STARE].nunique().reset_index()
        groupes.columns = [group_column, 'nombre_STR']

        # Left join pour conserver toutes les communes
        dff = toutes_communes.merge(
            groupes, on=group_column, how='left').fillna(0)
        dff['nombre_STR'] = dff['nombre_STR'].astype(int)

    else:
        resultats = df_NSTR[Data.ID_STARE].nunique()
        dff = pd.DataFrame({"nombre_STR": [resultats]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


# Nombre de STEU
def NSTEU(filtered_data, group_column):
    steu = {
        13: 'Genay', 6: 'Fontaines', 8: 'Jonage', 1: 'La Feyssine',
        11: 'Lissieu Le Bourg', 12: 'Lissieu Sémanet', 10: 'Meyzieu',
        5: 'Neuville', 7: 'Pierre-Bénite', 17: 'Quincieux',
        2: 'Saint-Fons', 4: 'Saint-Germain', 3: 'Givors'
    }

    dfsteu_bis = filtered_data[Data.QUERY_STEU].copy()
    dfsteu_bis[Data.NOM_STEU] = dfsteu_bis[Data.ID_STEU].map(
        steu).fillna(dfsteu_bis[Data.NOM_STEU])

    if group_column:
        # Liste complète des communes
        toutes_communes = filtered_data[Data.QUERY_CANAP][group_column].drop_duplicates(
        ).to_frame()

        # Comptage des STEU par commune
        groupes = dfsteu_bis.groupby(group_column)[
            Data.ID_STEU].nunique().reset_index()
        groupes.columns = [group_column, 'nombre_STEU']

        # Left join → on garde toutes les communes
        dff = toutes_communes.merge(
            groupes, on=group_column, how='left').fillna(0)
        dff['nombre_STEU'] = dff['nombre_STEU'].astype(int)

    else:
        # Mode global : nombre total de STEU
        resultats = dfsteu_bis[Data.ID_STEU].nunique()
        dff = pd.DataFrame({"nombre_STEU": [resultats]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


# Nombre de bassins enterrés et ciel ouvert
def NBEO(filtered_data, group_column):
    """
    Compte le nombre de bassins uniques de type 'ENT' et 'OUV'.

    Retourne un DataFrame avec une colonne pour le groupe, une pour le nombre
    de 'ENT' et une pour le nombre de 'OUV'.
    """
    # Isoler les données pour chaque type de nature
    df_OUV = filtered_data[filtered_data[Data.NATURE] == 'OUV']
    df_ENT = filtered_data[filtered_data[Data.NATURE] == 'ENT']

    # --- Cas 1 : Le calcul est groupé par une colonne ---
    if group_column:
        # Compter les identifiants uniques pour chaque groupe et chaque nature
        count_ent = df_ENT.groupby(group_column)[
            Data.ID_BASSIN].nunique().reset_index()
        count_ouv = df_OUV.groupby(group_column)[
            Data.ID_BASSIN].nunique().reset_index()

        # Renommer les colonnes de comptage avec les noms finaux désirés
        count_ent.columns = [group_column, 'nb_ENT']
        count_ouv.columns = [group_column, 'nb_OUV']

        # Fusionner les deux comptages horizontalement sur la colonne de groupe
        # 'outer' est utilisé pour conserver un groupe même s'il n'a qu'un seul type de nature
        dff = pd.merge(count_ent, count_ouv, on=group_column, how='outer')

        # Remplacer les NaN (cas où une nature n'existe pas pour un groupe) par 0
        dff = dff.fillna(0)

        # Assurer que les colonnes de comptage sont des entiers
        dff['nb_ENT'] = dff['nb_ENT'].astype(int)
        dff['nb_OUV'] = dff['nb_OUV'].astype(int)

    # --- Cas 2 : Le calcul est global ---
    else:
        nb_ent_total = df_ENT[Data.ID_BASSIN].nunique()
        nb_ouv_total = df_OUV[Data.ID_BASSIN].nunique()
        dff = pd.DataFrame(
            {'nb_ENT': [nb_ent_total], 'nb_OUV': [nb_ouv_total]})

    return dff


# Nombre de branchements
def NBr(filtered_data, group_column):
    if group_column:
        groupes = filtered_data[Data.QUERY_CANAS].groupby(group_column)
        indicateur_sum = groupes[Data.ID_CANAS].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, 'nbr_branch']
        dff = pd.DataFrame(resultats)

    else:
        resultats_list = [filtered_data[Data.QUERY_CANAS]
                          [Data.ID_CANAS].nunique()]
        dff = pd.DataFrame(resultats_list, columns=["nbr_branch"])
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Nombre de trémie


def NT(filtered_data, group_column):
    if group_column:
        groupes = filtered_data[Data.QUERY_TREMIE].groupby(group_column)
        indicateur_sum = groupes[Data.ID_TREMIE].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, 'nbr_trmie']
        dff = pd.DataFrame(resultats)

    else:
        resultats_list = [filtered_data[Data.QUERY_TREMIE]
                          [Data.ID_TREMIE].nunique()]
        dff = pd.DataFrame(resultats_list, columns=['nbr_trmie'])
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Nombre d'arbres de pluie


def NAP(filtered_data, group_column):
    df_bis = filtered_data[Data.QUERY_OGEP][filtered_data[Data.QUERY_OGEP]
                                            [Data.NATURE_OGEP] == 7].copy()
    if group_column:
        groupes = df_bis.groupby(group_column)
        indicateur_sum = groupes[Data.ID_OGEP].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, 'NBR_AP']
        dff = pd.DataFrame(resultats)

    else:
        resultats_list = [filtered_data[Data.QUERY_OGEP]
                          [filtered_data[Data.QUERY_OGEP][Data.NATURE_OGEP] == 7][Data.ID_OGEP].nunique()]
        dff = pd.DataFrame(resultats_list, columns=['NBR_AP'])
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Nombre de puits d'infiltration


def NPI(filtered_data, group_column):
    if group_column:
        groupes = filtered_data[Data.QUERY_PUITS].groupby(group_column)
        indicateur_sum = groupes[Data.ID_PUITSF].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, 'NBR_PI']
        dff = pd.DataFrame(resultats)

    else:
        resultats_list = [filtered_data[Data.QUERY_PUITS]
                          [Data.ID_PUITSF].nunique()]
        dff = pd.DataFrame(resultats_list, columns=['NBR_PI'])
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Nombre de FPR


def NFPR(filtered_data, group_column):
    # Filtrer les STEU qui sont des FPR (insensible à la casse)
    df_fpr = filtered_data[Data.QUERY_STEU].copy()
    df_fpr = df_fpr[df_fpr[Data.NOM_STEU].str.contains("Filtre planté de roseaux",
                                                       case=False, na=False)]

    if group_column:
        # Liste complète des communes (référence)
        communes = filtered_data[Data.QUERY_CANAP][group_column].drop_duplicates(
        ).to_frame()

        # Comptage des FPR par commune
        grp = (df_fpr.groupby(group_column)[Data.ID_STEU]
                     .nunique()
                     .reset_index())
        grp.columns = [group_column, 'NBR_FPR']

        # Left join pour conserver toutes les communes
        dff = communes.merge(grp, on=group_column, how='left').fillna(0)
        dff['NBR_FPR'] = dff['NBR_FPR'].astype(int)
    else:
        total = df_fpr[Data.ID_STEU].nunique()
        dff = pd.DataFrame({'NBR_FPR': [int(total)]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff


# Valeur patrimoniale à neuf Réseaux (Milliards d'euros)
def VPR(filtered_data, group_column, VP_RV, VP_RNV):
    """
    Calcule la valeur de l'indicateur VPR (réseaux visitables et non visitables).
    - Avec group_column : 1 ligne par commune, 0 si aucune donnée.
    - Sans group_column : valeur globale.
    """
    df_bis1 = filtered_data[Data.QUERY_CANAP][filtered_data[Data.QUERY_CANAP]
                                              [Data.HAUTEUR] >= 150].copy()
    df_bis2 = filtered_data[Data.QUERY_CANAP][filtered_data[Data.QUERY_CANAP]
                                              [Data.HAUTEUR] < 150].copy()

    if group_column:
        groupes1 = df_bis1.groupby(group_column)
        groupes2 = df_bis2.groupby(group_column)

        indicateur_sum = (
            (groupes1.apply(lambda x: x.drop_duplicates(subset=Data.ID_CANAP)[Data.LONGUEUR].sum()) * VP_RV) +
            (groupes2.apply(lambda x: x.drop_duplicates(
                subset=Data.ID_CANAP)[Data.LONGUEUR].sum()) * VP_RNV)
        ) / 1_000_000

        resultats = indicateur_sum.round(1).reset_index()
        resultats.columns = [group_column, Indicators.VALEUR]

        # Inclure toutes les communes même absentes
        all_groups = filtered_data[Data.QUERY_CANAP][group_column].drop_duplicates(
        ).to_frame()
        dff = all_groups.merge(
            resultats, on=group_column, how="left").fillna(0)

    else:
        resultat1 = df_bis1.drop_duplicates(subset=Data.ID_CANAP)[
            Data.LONGUEUR].sum()
        resultat2 = df_bis2.drop_duplicates(subset=Data.ID_CANAP)[
            Data.LONGUEUR].sum()
        valeur = round(
            ((resultat1 * VP_RV) + (resultat2 * VP_RNV)) / 1_000_000, 1)
        dff = pd.DataFrame([[valeur]], columns=[Indicators.VALEUR])

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


# Valeur patrimoniale à neuf Branchements (Milliards d'euros)
def VPBr(filtered_data, group_column, VP_branchement):
    if group_column:
        groupes = filtered_data[Data.QUERY_CANAS].groupby(group_column)
        indicateur_sum = round(
            groupes[Data.ID_CANAS].nunique() * VP_branchement/1000000, 1)
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, Indicators.VP_BRANCH]
        dff = pd.DataFrame(resultats)

    else:
        resultats = filtered_data[Data.QUERY_CANAS][Data.ID_CANAS].nunique(
        ) * VP_branchement / 1000000
        dff = pd.DataFrame([round(resultats, 1)],
                           columns=[Indicators.VP_BRANCH])
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Valeur patrimoniale à neuf arbres de pluie (k€)


def VPAP(filtered_data, VP_AP, group_column):
    df_bis = filtered_data[Data.QUERY_OGEP][filtered_data[Data.QUERY_OGEP]
                                            [Data.NATURE_OGEP] == 7].copy()
    if group_column:
        groupes = df_bis.groupby(group_column)
        indicateur_sum = round(groupes[Data.ID_OGEP].nunique() * VP_AP, 1)
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, Indicators.VP_AP_COL]
        dff = pd.DataFrame(resultats)

    else:
        resultats_list = [round(filtered_data[Data.QUERY_OGEP][filtered_data[Data.QUERY_OGEP]
                                [Data.NATURE_OGEP] == 7][Data.ID_OGEP].nunique() * VP_AP, 1)]
        dff = pd.DataFrame(resultats_list, columns=[Indicators.VP_AP_COL])
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Valeur patrimoniale à neuf puits d'infiltration (M€)


def VPPI(filtered_data, VP_PI, group_column):
    if group_column:
        groupes = filtered_data[Data.QUERY_PUITS].groupby(group_column)
        indicateur_sum = round(
            groupes[Data.ID_PUITSF].nunique() * VP_PI / 1000, 1)
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, Indicators.VP_PI_COL]
        dff = pd.DataFrame(resultats)

    else:
        resultats_list = [round(
            (filtered_data[Data.QUERY_PUITS][Data.ID_PUITSF].nunique()) * VP_PI / 1000, 1)]
        dff = pd.DataFrame(resultats_list, columns=[Indicators.VP_PI_COL])
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Linéaire de reseaux avec années de pose connues & estimées


def LRAPC(filtered_data, group_column):
    df_connues = filtered_data[Data.QUERY_CANAP][filtered_data[Data.QUERY_CANAP]
                                                 [Data.ANNEE_POSE].notna()].copy()
    df_estimees = filtered_data[Data.QUERY_CANAP][(filtered_data[Data.QUERY_CANAP][Data.ANNEE_POSE].isnull()) & (
        (filtered_data[Data.QUERY_CANAP][Data.ANNEE_POSE_SUP].notna()) | (filtered_data[Data.QUERY_CANAP][Data.ANNEE_POSE_INF].notna()))].copy()

    if group_column:
        groupes_connues = df_connues.groupby(group_column)
        groupes_estimees = df_estimees.groupby(group_column)
        df_tot = filtered_data[Data.QUERY_CANAP].groupby(group_column)

        resultats_connues = (round(groupes_connues.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000), 2)).reset_index()
        resultat_estimees = (round(groupes_estimees.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000), 2)).reset_index()
        indicateur_tot = df_tot.apply(lambda x: round(x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 2)).reset_index()

        resultats_connues.columns = [group_column, 'Longueur_connues']
        resultat_estimees.columns = [group_column, 'Longueur_estimees']
        indicateur_tot.columns = [group_column, 'longueur_tot']

        dff = pd.merge(pd.merge(resultats_connues, resultat_estimees, on=group_column,
                       how='outer'), indicateur_tot, on=group_column, how='outer')
        dff = dff.fillna(0)

        if dff.empty:
            dff['Pourcentage_connues'] = 0
            dff['Pourcentage_estimees'] = 0
        else:
            dff['Pourcentage_connues'] = round(
                (dff['Longueur_connues'] * 100)/dff['longueur_tot'], 2)
            dff['Pourcentage_estimees'] = round(
                (dff['Longueur_estimees'] * 100)/dff['longueur_tot'], 2)
    else:
        tot = round(filtered_data[Data.QUERY_CANAP].drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 2)
        resultat_connues = round(df_connues.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 2)
        resultat_estimees = round(df_estimees.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 2)

        pourcentage_connues = round(
            (resultat_connues * 100)/tot, 2) if tot > 0 else 0
        pourcentage_estimees = round(
            (resultat_estimees * 100)/tot, 2) if tot > 0 else 0

        dff = pd.DataFrame({'Longueur_connues': [resultat_connues], 'Pourcentage_connues': [
                           pourcentage_connues], 'Longueur_estimees': [resultat_estimees], 'Pourcentage_estimees': [pourcentage_estimees]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Age moyen de réseaux


def AMR(filtered_data, group_column):
    year = datetime.now().year
    df = filtered_data[Data.QUERY_CANAP].copy()

    total = len(df)

    # Exclure NaN, 0, et doublons
    df_known = df[df[Data.ANNEE_POSE].notna()]
    df_known = df_known[df_known[Data.ANNEE_POSE].astype(float) > 1800]  # exclut 0 et aberrants
    df_known = df_known.drop_duplicates(subset=Data.ID_CANAP)
    df_known['age'] = year - df_known[Data.ANNEE_POSE].astype(float).astype(int)
    df_known = df_known[(df_known['age'] >= 0) & (df_known['age'] <= 200)]

    pct_connu = round(100 * len(df_known) / total, 1) if total else 0
    print(f"⚠️  AMR calculé sur {len(df_known)}/{total} canalisations ({pct_connu}% avec année connue)")

    if group_column:
        dff = (df_known.groupby(group_column)['age']
                       .mean()
                       .round(1)
                       .reset_index())
        dff.columns = [group_column, 'moy_age']
    else:
        dff = pd.DataFrame([[round(df_known['age'].mean(), 1)]], columns=['moy_age'])

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff


def AMR_ESTIME(filtered_data, group_column):
    """
    Calcule l'âge moyen du réseau en combinant :
    - Années connues  : ANNEE_POSE renseignée et > 1800
    - Années estimées : ANNEE_POSE absente/invalide mais ANNEE_POSE_SUP ou INF dispo,
                        avec SUP et INF > 1800 (filtre les estimations aberrantes du ML)
    """
    year = datetime.now().year
    df = filtered_data[Data.QUERY_CANAP].copy()
    df = df.drop_duplicates(subset=Data.ID_CANAP)

    # ── Masque connu : ANNEE_POSE présente et plausible ───────────────────────
    mask_connu = (
        df[Data.ANNEE_POSE].notna() &
        (df[Data.ANNEE_POSE].astype(float) > 1800)
    )

    # ── Masque estimé : pas d'ANNEE_POSE valide, mais SUP ou INF disponible ──
    annee_pose_invalide = (
        df[Data.ANNEE_POSE].isna() |
        (df[Data.ANNEE_POSE].astype(float) <= 1800)
    )
    mask_estime = (
        annee_pose_invalide &
        (df[Data.ANNEE_POSE_SUP].notna() | df[Data.ANNEE_POSE_INF].notna())
    )

    df['annee_retenue'] = float('nan')

    # Connu → ANNEE_POSE directement
    df.loc[mask_connu, 'annee_retenue'] = df.loc[mask_connu, Data.ANNEE_POSE].astype(float)

    # Estimé → milieu de [INF, SUP], en ignorant les bornes aberrantes
    if mask_estime.any():
        sup_raw = df.loc[mask_estime, Data.ANNEE_POSE_SUP].astype(float)
        inf_raw = df.loc[mask_estime, Data.ANNEE_POSE_INF].astype(float)

        # Remplacer les bornes aberrantes par NaN 
        sup = sup_raw.where(sup_raw > 1800)
        inf = inf_raw.where(inf_raw > 1800)

        # Moyenne des bornes valides : si les deux → (sup+inf)/2, si une seule → celle-là
        annee_estimee = (sup.fillna(inf) + inf.fillna(sup)) / 2

        df.loc[mask_estime, 'annee_retenue'] = annee_estimee

    # ── Filtres finaux ────────────────────────────────────────────────────────
    df = df[df['annee_retenue'].notna()]
    df = df[df['annee_retenue'] > 1800]
    df['age'] = year - df['annee_retenue'].astype(float)
    df = df[(df['age'] >= 0) & (df['age'] <= 200)]

    if df.empty:
        if group_column:
            return pd.DataFrame(columns=[group_column, 'moy_age_estime'])
        else:
            return pd.DataFrame([[None]], columns=['moy_age_estime'])

    if group_column:
        dff = (df.groupby(group_column)['age']
                  .mean()
                  .round(1)
                  .reset_index())
        dff.columns = [group_column, 'moy_age_estime']
    else:
        dff = pd.DataFrame(
            [[round(df['age'].mean(), 1)]],
            columns=['moy_age_estime']
        )

    return dff

# Age médian des réseaux


def AMeR(filtered_data, group_column):
    ages = []
    df = []
    year = datetime.now().year
    for index, row in filtered_data[Data.QUERY_CANAP].iterrows():
        if (not pd.isnull(row[Data.ANNEE_POSE])) and (int(row[Data.ANNEE_POSE]) != 0):
            ages.append((row[Data.ID_CANAP], year - int(row[Data.ANNEE_POSE])))
            df.append(row)
    df_bis = pd.DataFrame(df)
    df_ages = pd.DataFrame(ages)
    df_ages.columns = [Data.ID_CANAP, 'ages']
    df_bis = pd.merge(df_bis, df_ages, on=Data.ID_CANAP, how='left')
    if group_column:
        groupes = df_bis.groupby([group_column])
        indicateur_med = round(groupes.apply(
            lambda x: x.drop_duplicates(subset=Data.ID_CANAP)['ages'].median()), 0)
        resultats = indicateur_med.reset_index()
        resultats.columns = [group_column, 'med_age']
        dff = pd.DataFrame(resultats)
        dff = dff.fillna(0)

    else:
        resultats_list = [round(df_bis.drop_duplicates(
            subset=Data.ID_CANAP)['ages'].median(), 0)]
        dff = pd.DataFrame(resultats_list, columns=['med_age'])

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff


def APSTR(filtered_data, group_column):
    if group_column:
        groupes = filtered_data[Data.QUERY_STARE].groupby(
            [group_column, Data.ANNEE_CONSTRUCTION])
        indicateur_sum = groupes[Data.ID_STARE].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, Data.ANNEE_CONSTRUCTION, 'nb_stare']
        dff = pd.DataFrame(resultats)

    else:
        groupes = filtered_data[Data.QUERY_STARE].groupby(
            Data.ANNEE_CONSTRUCTION)
        indicateur_sum = groupes[Data.ID_STARE].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [Data.ANNEE_CONSTRUCTION, 'nb_stare']
        dff = pd.DataFrame(resultats)
    dff[Data.ANNEE_CONSTRUCTION] = dff[Data.ANNEE_CONSTRUCTION].apply(
        lambda x: int(x))
    dff[Data.ANNEE_CONSTRUCTION][dff[Data.ANNEE_CONSTRUCTION] == 0] = None

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Année de mise en place des STEU


def APSTEU(filtered_data, group_column):
    steu = {
        13: 'Genay', 6: 'Fontaines', 8: 'Jonage', 1: 'La Feyssine',
        11: 'Lissieu Le Bourg', 12: 'Lissieu Sémanet', 10: 'Meyzieu',
        5: 'Neuville', 7: 'Pierre-Bénite', 17: 'Quincieux',
        2: 'Saint-Fons', 4: 'Saint-Germain', 3: 'Givors'
    }
    dfsteu_bis = filtered_data[Data.QUERY_STEU].copy()
    dfsteu_bis[Data.NOM_STEU] = dfsteu_bis[Data.ID_STEU].map(
        steu).fillna(dfsteu_bis[Data.NOM_STEU])
    if group_column:
        groupes = dfsteu_bis.groupby([group_column, Data.ANNEE_CONSTRUCTION])
        indicateur_sum = groupes[Data.ID_STEU].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, Data.ANNEE_CONSTRUCTION, 'nb_steu']

    else:
        groupes = dfsteu_bis.groupby(Data.ANNEE_CONSTRUCTION)
        indicateur_sum = groupes[Data.ID_STEU].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [Data.ANNEE_CONSTRUCTION, 'nb_steu']
    dff = pd.DataFrame(resultats)
    dff[Data.ANNEE_CONSTRUCTION] = dff[Data.ANNEE_CONSTRUCTION].apply(
        lambda x: int(x))
    dff[Data.ANNEE_CONSTRUCTION][dff[Data.ANNEE_CONSTRUCTION] == 0] = None
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Linéaire de réseaux en classe A, B et C


def LinClass(filtered_data, group_column):
    df_A = filtered_data[Data.QUERY_CANAP][filtered_data[Data.QUERY_CANAP]
                                           [Data.PRECISION_PLANIMETRIQUE].isin([0, 1, 2, 3])].copy()
    df_B = filtered_data[Data.QUERY_CANAP][filtered_data[Data.QUERY_CANAP]
                                           [Data.PRECISION_PLANIMETRIQUE] == 4].copy()
    df_C = filtered_data[Data.QUERY_CANAP][filtered_data[Data.QUERY_CANAP]
                                           [Data.PRECISION_PLANIMETRIQUE] == 5].copy()

    if group_column:
        groupesA = df_A.groupby(group_column)
        groupesB = df_B.groupby(group_column)
        groupesC = df_C.groupby(group_column)
        df_tot = filtered_data[Data.QUERY_CANAP].groupby(group_column)

        resultatsA = (round(groupesA.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000), 2)).reset_index()
        resultatsB = (round(groupesB.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000), 2)).reset_index()
        resultatsC = (round(groupesC.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000), 2)).reset_index()
        indicateur_tot = df_tot.apply(lambda x: round(x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 2)).reset_index()

        resultatsA.columns = [group_column, 'longueur_sum_A']
        resultatsB.columns = [group_column, 'longueur_sum_B']
        resultatsC.columns = [group_column, 'longueur_sum_C']
        indicateur_tot.columns = [group_column, 'longueur_tot']

        dff = pd.merge(pd.merge(pd.merge(resultatsA, resultatsB, on=group_column, how='outer'),
                       resultatsC, on=group_column, how='outer'), indicateur_tot, on=group_column, how='outer')
        dff = dff.fillna(0)
        if dff.empty:
            dff['Pourcentage_A'] = 0
            dff['Pourcentage_B'] = 0
            dff['Pourcentage_C'] = 0
        else:
            dff['Pourcentage_A'] = round(
                (dff['longueur_sum_A'] * 100)/dff['longueur_tot'], 2)
            dff['Pourcentage_B'] = round(
                (dff['longueur_sum_B'] * 100)/dff['longueur_tot'], 2)
            dff['Pourcentage_C'] = round(
                (dff['longueur_sum_C'] * 100)/dff['longueur_tot'], 2)
    else:
        tot = round(filtered_data[Data.QUERY_CANAP].drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, 2)
        resultatsA = round(df_A.drop_duplicates(subset=Data.ID_CANAP)[
                           Data.LONGUEUR].sum()/1000, 2)
        resultatsB = round(df_B.drop_duplicates(subset=Data.ID_CANAP)[
                           Data.LONGUEUR].sum()/1000, 2)
        resultatsC = round(df_C.drop_duplicates(subset=Data.ID_CANAP)[
                           Data.LONGUEUR].sum()/1000, 2)

        dff = pd.DataFrame({'longueur_sum_A': [resultatsA], 'Pourcentage_A': [round(resultatsA*100/tot, 2) if tot > 0 else 0],
                            'longueur_sum_B': [resultatsB], 'Pourcentage_B':  [round(resultatsB*100/tot, 2) if tot > 0 else 0],
                            'longueur_sum_C': [resultatsC], 'Pourcentage_C':  [round(resultatsC*100/tot, 2) if tot > 0 else 0]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Linéaire de réseaux visitables- inspection (DIAG et PREDIAG)


def LDiagPrediag(df_vis, group_column, group_list, et_2_bis_value):
    """
    Calcule les linéaires de diagnostic et pré-diagnostic, globalement ou par groupe.
    """
    # Filtrage initial des données pour ne garder que le nécessaire
    df_total = df_vis.filter(
        items=[Data.ID_CANAP, 'ET_2', 'ET_2_BIS', Data.LONGUEUR, group_column])

    # Données pour le total cumulé
    df_et_2_bis = df_total[df_total['ET_2_BIS'] == et_2_bis_value]

    # Données pour le réalisé dans l'année N-1
    df_year = df_total[(df_total['ET_2'] == datetime.now().year - 1)
                       & (df_total['ET_2_BIS'] == et_2_bis_value)]

    # --- Cas 1 : Le calcul est groupé par une colonne ---
    if group_column:
        # Optimisation : on supprime les doublons en gardant la colonne de groupe AVANT l'agrégation
        total_unique = df_total.drop_duplicates(
            subset=[group_column, Data.ID_CANAP])
        cumul_unique = df_et_2_bis.drop_duplicates(
            subset=[group_column, Data.ID_CANAP])
        year_unique = df_year.drop_duplicates(
            subset=[group_column, Data.ID_CANAP])

        # Calcul des sommes par groupe
        total_by_group = total_unique.groupby(
            group_column)[Data.LONGUEUR].sum().div(1000)
        cumul_by_group = cumul_unique.groupby(
            group_column)[Data.LONGUEUR].sum().div(1000)
        year_by_group = year_unique.groupby(
            group_column)[Data.LONGUEUR].sum().div(1000)

        # Création du DataFrame final en combinant les séries de résultats
        dff = pd.DataFrame({
            Data.TOTAL: total_by_group,
            Data.REALISE_DANS_L_ANNEE: year_by_group,
            Data.TOTAL_CUMULE: cumul_by_group
        })

        # S'assurer que tous les groupes de la liste sont présents, même avec 0
        dff = dff.reindex(group_list).fillna(0)

        # Calcul du pourcentage avec gestion de la division par zéro
        total_non_nul = dff[Data.TOTAL] > 0
        dff[Indicators.POURCENTAGE] = 0
        dff.loc[total_non_nul, Indicators.POURCENTAGE] = \
            (dff.loc[total_non_nul, Data.TOTAL_CUMULE] * 100) / \
            dff.loc[total_non_nul, Data.TOTAL]

        # Conversion de toutes les colonnes en entier pour un affichage propre
        dff = dff.astype(np.int64)

        return dff.reset_index().rename(columns={'index': group_column})

    # --- Cas 2 : Le calcul est global (déjà implémenté) ---
    else:
        longueur_elements_concernes = df_total.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].div(1000).sum().astype(np.int64)
        longueur_elements_realises_depuis_1990 = df_et_2_bis.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].div(1000).sum().astype(np.int64)

        resultats = [[
            longueur_elements_concernes,
            df_year.drop_duplicates(subset=Data.ID_CANAP)[
                Data.LONGUEUR].div(1000).sum().astype(np.int64),
            longueur_elements_realises_depuis_1990,
            ((longueur_elements_realises_depuis_1990 * 100) /
             longueur_elements_concernes).astype(np.int64) if longueur_elements_concernes != 0 else 0
        ]]

        dff = pd.DataFrame(resultats, columns=[
                           Data.TOTAL, Data.REALISE_DANS_L_ANNEE, Data.TOTAL_CUMULE, Indicators.POURCENTAGE])
        dff.index = [et_2_bis_value]

        return dff


def LRSFa(gdf_glob, group_column):
    """
    Calcule les linéaires de réseaux secs courant faible et fort.
    Version corrigée pour gérer la conversion de type et la division par zéro.
    """
    # Filtrer les données par type de réseau
    gdf_Fa = gdf_glob[gdf_glob["typereseausec"] == Data.FAIBLE].copy()
    gdf_Fo = gdf_glob[gdf_glob["typereseausec"] == Data.FORT].copy()

    # --- Cas 1 : Calcul par groupe ---
    if group_column:
        # Groupement pour les réseaux faibles
        df_fa_grouped = gdf_Fa.groupby(group_column)[
            'longueur_troncon'].sum().reset_index()
        df_fa_grouped.columns = [group_column, Indicators.LONGUEUR_RSEC_FAIBLE]

        # Groupement pour les réseaux forts
        df_fo_grouped = gdf_Fo.groupby(group_column)[
            'longueur_troncon'].sum().reset_index()
        df_fo_grouped.columns = [group_column, Indicators.LONGUEUR_RSEC_FORT]

        # Fusion des résultats
        dff = pd.merge(df_fa_grouped, df_fo_grouped,
                       on=group_column, how='outer')

        # On supprime la colonne 'index' inutile si elle existe
        if 'index' in dff.columns:
            dff = dff.drop(columns=['index'])

        # Remplir les valeurs manquantes par 0
        dff = dff.fillna(0)

        # Conversion en entier pour éviter les décimales
        dff[Indicators.LONGUEUR_RSEC_FAIBLE] = dff[Indicators.LONGUEUR_RSEC_FAIBLE].astype(
            int)
        dff[Indicators.LONGUEUR_RSEC_FORT] = dff[Indicators.LONGUEUR_RSEC_FORT].astype(
            int)

        if not dff.empty:
            # Calcul du total
            dff[Indicators.TOTAL] = dff[Indicators.LONGUEUR_RSEC_FAIBLE] + \
                dff[Indicators.LONGUEUR_RSEC_FORT]

            # Initialiser les colonnes de pourcentage avec des valeurs par défaut
            dff[Indicators.POURCENTAGE_FA] = 0
            dff[Indicators.POURCENTAGE_FO] = 0
            dff[Indicators.POURCENTAGE_TOT] = 0

            # Créer un masque pour les lignes où le total est non nul
            non_zero_mask = dff[Indicators.TOTAL] > 0

            if non_zero_mask.any():  # Vérifier s'il y a au moins une ligne avec total > 0
                # Calculer les pourcentages uniquement sur ces lignes
                percentage_fa = (dff.loc[non_zero_mask, Indicators.LONGUEUR_RSEC_FAIBLE]
                                 * 100) / dff.loc[non_zero_mask, Indicators.TOTAL]
                percentage_fo = (dff.loc[non_zero_mask, Indicators.LONGUEUR_RSEC_FORT]
                                 * 100) / dff.loc[non_zero_mask, Indicators.TOTAL]

                # Assigner les résultats et convertir en entier
                dff.loc[non_zero_mask, Indicators.POURCENTAGE_FA] = round(
                    percentage_fa).astype(int)
                dff.loc[non_zero_mask, Indicators.POURCENTAGE_FO] = round(
                    percentage_fo).astype(int)
                # Le total fait toujours 100%
                dff.loc[non_zero_mask, Indicators.POURCENTAGE_TOT] = 100
        else:
            # Si le dataframe est vide après la fusion, on s'assure qu'il a les bonnes colonnes
            dff[Indicators.TOTAL] = 0
            dff[Indicators.POURCENTAGE_FA] = 0
            dff[Indicators.POURCENTAGE_FO] = 0
            dff[Indicators.POURCENTAGE_TOT] = 0

        return dff

    # --- Cas 2 : Calcul global ---
    else:
        # Calcul des longueurs totales
        longueur_fa = int(gdf_Fa['longueur_troncon'].sum())
        longueur_fo = int(gdf_Fo['longueur_troncon'].sum())
        total = longueur_fa + longueur_fo

        # Calcul des pourcentages
        pourcentage_fa = 0
        pourcentage_fo = 0
        pourcentage_tot = 0

        if total > 0:
            pourcentage_fa = int(round(longueur_fa * 100 / total))
            pourcentage_fo = int(round(longueur_fo * 100 / total))
            pourcentage_tot = 100  # Le total fait toujours 100%

        # Création du DataFrame résultat
        dff = pd.DataFrame({
            Indicators.LONGUEUR_RSEC_FAIBLE: [longueur_fa],
            Indicators.LONGUEUR_RSEC_FORT: [longueur_fo],
            Indicators.TOTAL: [total],
            Indicators.POURCENTAGE_FA: [pourcentage_fa],
            Indicators.POURCENTAGE_FO: [pourcentage_fo],
            Indicators.POURCENTAGE_TOT: [pourcentage_tot]
        })

    return dff

# Linéaire de réseaux secs en classe A, B et C


def LinSecClass(gdf_glob, filtered_data, group_column):
    gdf_A = gdf_glob[gdf_glob["classeprecision"] == Data.CLASSE_A].copy()
    gdf_B = gdf_glob[gdf_glob["classeprecision"] == Data.CLASSE_B].copy()
    gdf_C = gdf_glob[gdf_glob["classeprecision"] == Data.CLASSE_C].copy()
    tot = gdf_glob[gdf_glob["classeprecision"].notna()
                   ]['longueur_troncon'].sum()

    if group_column:
        groupesA = gdf_A.groupby(group_column)
        groupesB = gdf_B.groupby(group_column)
        groupesC = gdf_C.groupby(group_column)

        A = (groupesA['longueur_troncon'].sum()).reset_index()
        B = (groupesB['longueur_troncon'].sum()).reset_index()
        C = (groupesC['longueur_troncon'].sum()).reset_index()

        A.columns = [group_column, 'longueur_sum_A']
        B.columns = [group_column, 'longueur_sum_B']
        C.columns = [group_column, 'longueur_sum_C']

        dff = pd.merge(pd.merge(pd.merge(A, B, on=group_column, how='outer'), C, on=group_column, how='outer'),
                       pd.DataFrame(filtered_data[Data.QUERY_RESEAU_SEC].groupby(group_column)[
                                    'identifiantreseausec'].count()).reset_index().rename(columns={'identifiantreseausec': 'tot'}),
                       on=group_column, how='outer')
        dff = dff.fillna(0)

        if dff.empty:
            dff['Pourcentage_A'] = 0
            dff['Pourcentage_B'] = 0
            dff['Pourcentage_C'] = 0
        else:
            dff['Pourcentage_A'] = (
                dff['longueur_sum_A'] * 100 / dff['tot']).astype(int)
            dff['Pourcentage_B'] = (
                dff['longueur_sum_B'] * 100 / dff['tot']).astype(int)
            dff['Pourcentage_C'] = (
                dff['longueur_sum_C'] * 100 / dff['tot']).astype(int)
    else:
        resultatsA = [int(gdf_A["longueur_troncon"].sum()), int(
            gdf_A["longueur_troncon"].sum()*100/tot) if tot > 0 else 0]
        resultatsB = [int(gdf_B["longueur_troncon"].sum()), int(
            gdf_B["longueur_troncon"].sum()*100/tot) if tot > 0 else 0]
        resultatsC = [int(gdf_C["longueur_troncon"].sum()), int(
            gdf_C["longueur_troncon"].sum()*100/tot) if tot > 0 else 0]

        dff = pd.DataFrame({'longueur_sum_A': [resultatsA[0]], 'longueur_sum_B': [resultatsB[0]], 'longueur_sum_C': [resultatsC[0]],
                            'Pourcentage_A': [resultatsA[1]], 'Pourcentage_B': [resultatsB[1]], 'Pourcentage_C': [resultatsC[1]]})
    dff = dff.fillna(0)
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Linéaire d'ITV


def LITV(filtered_data, valeurs_uniques, valeurs_uniques_annuelles, group_column):
    df_total = filtered_data[Data.QUERY_CANAP][filtered_data[Data.QUERY_CANAP]
                                               [Data.ID_CANAP].isin(valeurs_uniques)].copy()
    df_year = filtered_data[Data.QUERY_CANAP][filtered_data[Data.QUERY_CANAP]
                                              [Data.ID_CANAP].isin(valeurs_uniques_annuelles)].copy()

    if group_column:
        groupes = filtered_data[Data.QUERY_CANAP].groupby(group_column)
        groupes_total = df_total.groupby(group_column)
        groupes_year = df_year.groupby(group_column)

        if groupes.ngroups != 0:
            indicateur_sum = (round(groupes.apply(lambda x: x.drop_duplicates(
                subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000))).reset_index()
            indicateur_sum.columns = [group_column, Data.TOTAL]
        else:
            indicateur_sum = pd.DataFrame(columns=[group_column, Data.TOTAL])
        if groupes_total.ngroups != 0:
            resultats_total = (round(groupes_total.apply(lambda x: x.drop_duplicates(
                subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000))).reset_index()
            resultats_total.columns = [group_column, Data.TOTAL_CUMULE]
        else:
            resultats_total = pd.DataFrame(
                columns=[group_column, Data.TOTAL_CUMULE])
        # Vérifie si le GroupBy a des groupes (pas vide)
        if groupes_year.ngroups != 0:
            resultats_year = (round(groupes_year.apply(lambda x: x.drop_duplicates(
                subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000))).reset_index()
            resultats_year.columns = [group_column, Data.REALISE_DANS_L_ANNEE]
        else:
            resultats_year = pd.DataFrame(
                columns=[group_column, Data.REALISE_DANS_L_ANNEE])

        dff = pd.merge(indicateur_sum, pd.merge(resultats_year, resultats_total,
                       on=group_column, how='outer'), on=group_column, how='outer')
        dff = dff.fillna(0)

        if dff.empty:
            dff['Pourcentage_itv'] = 0
        else:
            dff['Pourcentage_itv'] = (
                dff[Data.TOTAL_CUMULE]*100) / dff[Data.TOTAL]
            dff = dff.fillna(0)
    else:
        total_longueur = filtered_data[Data.QUERY_CANAP].drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()
        realise_annee = df_year.drop_duplicates(subset=Data.ID_CANAP)[
            Data.LONGUEUR].sum()
        total_cumule = df_total.drop_duplicates(subset=Data.ID_CANAP)[
            Data.LONGUEUR].sum()

        pourcentage_itv = int((total_cumule * 100) /
                              total_longueur) if total_longueur > 0 else 0

        dff = pd.DataFrame({Data.TOTAL: [int(total_longueur/1000)],
                            Data.REALISE_DANS_L_ANNEE: [int(realise_annee/1000)],
                            Data.TOTAL_CUMULE: [int(total_cumule/1000)],
                            'Pourcentage_itv': [pourcentage_itv]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff

# Nombre d'inspection sur les STEU


def NISTEU(filtered_data, ins_steu, group_column):
    # --- Période : l'année N-1 ---
    current_year = datetime.now().year
    date_debut = datetime(current_year - 1, 1, 1)
    date_fin = datetime(current_year - 1, 12, 31)

    # --- Préparation des données d'installation (ins_steu) ---
    ins = ins_steu.copy()
    # Extraire le numéro avant " - " dans "N° - Nom Station"
    ins['N°'] = ins['N° - Nom Station'].astype(
        str).str.split(' - ').str[0].str.strip()
    ins = ins.rename(columns={'Création': 'Date_ins'})
    ins['Date_ins'] = pd.to_datetime(
        ins['Date_ins'], dayfirst=True, errors='coerce')

    # --- Préparation des données STEU du référentiel ---
    dfq = filtered_data[Data.QUERY_STEU].copy()

    # Extraction manuelle d'un code depuis NOM_STEU si présent sous la forme "... Code<XXX>_ ..."
    def extract_code(nomsteu):
        if isinstance(nomsteu, str) and "Code" in nomsteu and "_" in nomsteu:
            part = nomsteu.split("Code", 1)[1]
            code = part.split("_", 1)[0].strip()
            return code if code else None
        return None

    # Harmoniser la clé 'N°' dans dfq
    if 'N°' not in dfq.columns:
        dfq['N°'] = dfq[Data.NOM_STEU].apply(extract_code)

    # Forcer en str pour merger de façon robuste
    ins['N°'] = ins['N°'].astype(str)
    dfq['N°'] = dfq['N°'].astype(str)

    # --- Jointure installations ↔ référentiel STEU ---
    merged = pd.merge(ins[['N°', 'Date_ins']], dfq, on='N°', how='inner')

    # --- Calculs ---
    if group_column:
        # 1) Liste complète des groupes (ex. toutes les communes)
        groups_all = (
            filtered_data[Data.QUERY_CANAP][group_column]
            .drop_duplicates()
            .to_frame()
        )

        # 2) Totaux par groupe (toutes les STEU connues)
        total = (
            dfq.groupby(group_column)['N°']
               .nunique()
               .reset_index(name=Data.TOTAL)
        )

        # 3) Total cumulé (toutes les installations présentes dans 'merged', toutes dates)
        total_cumule = (
            merged.groupby(group_column)['N°']
                  .nunique()
                  .reset_index(name=Data.TOTAL_CUMULE)
        )

        # 4) Réalisé dans l’année N-1
        merged_year = merged[merged['Date_ins'].between(date_debut, date_fin)]
        realise_annee = (
            merged_year.groupby(group_column)['N°']
                       .nunique()
                       .reset_index(name=Data.REALISE_DANS_L_ANNEE)
        )

        # 5) Assemblage avec conservation de tous les groupes
        dff = (groups_all
               .merge(total, on=group_column, how='left')
               .merge(realise_annee, on=group_column, how='left')
               .merge(total_cumule, on=group_column, how='left')
               .fillna({Data.TOTAL: 0,
                        Data.REALISE_DANS_L_ANNEE: 0,
                        Data.TOTAL_CUMULE: 0}))

        # 6) Pourcentage (éviter division par zéro)
        dff[Data.POURCENTAGE_INS] = 0.0
        mask = dff[Data.TOTAL] > 0
        dff.loc[mask, Data.POURCENTAGE_INS] = (
            (dff.loc[mask, Data.REALISE_DANS_L_ANNEE]
             * 100.0) / dff.loc[mask, Data.TOTAL]
        ).round(2)

    else:
        merged_year = merged[merged['Date_ins'].between(date_debut, date_fin)]
        total = dfq['N°'].nunique()
        total_cumule = merged['N°'].nunique()
        realise_annee = merged_year['N°'].nunique()
        pourcentage = round((realise_annee * 100.0 / total),
                            2) if total > 0 else 0.0

        dff = pd.DataFrame({
            Data.TOTAL: [int(total)],
            Data.REALISE_DANS_L_ANNEE: [int(realise_annee)],
            Data.TOTAL_CUMULE: [int(total_cumule)],
            Data.POURCENTAGE_INS: [pourcentage]
        })

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


# Nombre d'inspection sur les STR
def NISTR(filtered_data, ins_str, group_column):
    current_year = datetime.now().year
    date_debut = datetime(current_year - 1, 1, 1)
    date_fin = datetime(current_year - 1, 12, 31)

    # --- Prépare les données d'inspection (ins_str) ---
    ins = ins_str.copy()
    # Un enregistrement par (N°, Création)
    ins = (ins.groupby(['N°', 'Création']).first().reset_index()
              .rename(columns={'Création': 'Date_ins'}))
    ins['N°'] = ins['N°'].astype(str)
    ins['Date_ins'] = pd.to_datetime(
        ins['Date_ins'], dayfirst=True, errors='coerce')

    # --- Prépare les données des stations (référentiel STR) ---
    df_stations = filtered_data[Data.QUERY_STARE].copy()
    df_stations = df_stations[df_stations[Data.NUMERO].notna() & (
        df_stations[Data.NUMERO] != 0)]
    df_stations['N°'] = df_stations[Data.NUMERO].astype(str)

    # --- Jointure : stations qui ont des inspections ---
    df_merged = pd.merge(ins[['N°', 'Date_ins']],
                         df_stations, on='N°', how='inner')

    if group_column:
        # 1) liste complète des groupes (ex. toutes les communes)
        all_groups = (
            filtered_data[Data.QUERY_CANAP][group_column]
            .drop_duplicates()
            .to_frame()
        )

        # 2) Total stations distinctes par groupe
        total = (df_stations.groupby(group_column)['N°']
                 .nunique()
                 .reset_index(name=Data.TOTAL))

        # 3) Total cumulé (toutes inspections connues)
        total_cumule = (df_merged.groupby(group_column)['N°']
                        .nunique()
                        .reset_index(name=Data.TOTAL_CUMULE))

        # 4) Réalisé sur l'année N-1
        df_year = df_merged[df_merged['Date_ins'].between(
            date_debut, date_fin)]
        realise_annee = (df_year.groupby(group_column)['N°']
                         .nunique()
                         .reset_index(name=Data.REALISE_DANS_L_ANNEE))

        # 5) Assemblage en gardant tous les groupes
        dff = (all_groups
               .merge(total, on=group_column, how='left')
               .merge(realise_annee, on=group_column, how='left')
               .merge(total_cumule, on=group_column, how='left')
               .fillna({Data.TOTAL: 0, Data.REALISE_DANS_L_ANNEE: 0, Data.TOTAL_CUMULE: 0}))

        # 6) % réalisé
        dff[Data.POURCENTAGE_INS] = 0.0
        mask = dff[Data.TOTAL] > 0
        dff.loc[mask, Data.POURCENTAGE_INS] = (
            dff.loc[mask, Data.REALISE_DANS_L_ANNEE] *
            100.0 / dff.loc[mask, Data.TOTAL]
        ).round(2)

        # Cast propres
        dff[Data.TOTAL] = dff[Data.TOTAL].astype(int)
        dff[Data.REALISE_DANS_L_ANNEE] = dff[Data.REALISE_DANS_L_ANNEE].astype(
            int)
        dff[Data.TOTAL_CUMULE] = dff[Data.TOTAL_CUMULE].astype(int)

        dff = dff.reset_index(drop=True)

    else:
        total = df_stations['N°'].nunique()
        df_year = df_merged[df_merged['Date_ins'].between(
            date_debut, date_fin)]
        realise_annee = df_year['N°'].nunique()
        total_cumule = df_merged['N°'].nunique()
        pourcentage = round((realise_annee * 100.0 / total),
                            2) if total > 0 else 0.0

        dff = pd.DataFrame({
            Data.TOTAL: [int(total)],
            Data.REALISE_DANS_L_ANNEE: [int(realise_annee)],
            Data.TOTAL_CUMULE: [int(total_cumule)],
            Data.POURCENTAGE_INS: [pourcentage]
        })

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


# Nombre d'inspection sur les trémies
def NITREMIES(filtered_data, ins_tremies, group_column, date_debut, date_fin):
    ins_tremies_grp = ins_tremies.groupby(['N°', 'Création'])
    df_tremies = ins_tremies_grp.first().reset_index()
    df_tremies = df_tremies.rename(
        columns={'N°': Data.NUMERO, 'Création': 'Date_ins'})
    df_tremies = df_tremies[[Data.NUMERO, 'Date_ins']]
    df_tremies[Data.NUMERO] = df_tremies[Data.NUMERO].astype(int)
    # Joindre les deux dataframes
    df_merged = pd.merge(
        df_tremies, filtered_data[Data.QUERY_TREMIE], on=Data.NUMERO, how='inner')
    df_merged['Date_ins'] = pd.to_datetime(
        df_merged['Date_ins'], dayfirst=True, errors='coerce')

    if group_column:
        df_year = df_merged[(df_merged['Date_ins'] >= date_debut) & (
            df_merged['Date_ins'] <= date_fin)].copy()
        groupes = filtered_data[Data.QUERY_TREMIE].groupby(group_column)
        groupes_total = df_merged.groupby(group_column)
        groupes_year = df_year.groupby(group_column)

        total = (groupes[Data.NUMERO].nunique()).reset_index()
        resultats_total = (groupes_total[Data.NUMERO].nunique()).reset_index()
        resultats_year = (groupes_year[Data.NUMERO].nunique()).reset_index()

        total.columns = [group_column, Data.TOTAL]
        resultats_total.columns = [group_column, Data.TOTAL_CUMULE]
        resultats_year.columns = [group_column, Data.REALISE_DANS_L_ANNEE]

        dff = pd.merge(total, pd.merge(resultats_year, resultats_total,
                       on=group_column, how='right'),  on=group_column)
        dff = dff.fillna(0)

        if dff.empty:
            dff[Data.POURCENTAGE_INS] = 0
        else:
            dff[Data.POURCENTAGE_INS] = int(
                (dff[Data.REALISE_DANS_L_ANNEE]*100) / dff[Data.TOTAL])
    else:
        tot_year = df_merged[(df_merged['Date_ins'] >= date_debut) & (
            df_merged['Date_ins'] <= date_fin)][Data.NUMERO].nunique()
        tot = df_merged[Data.NUMERO].nunique()
        Total = filtered_data[Data.QUERY_TREMIE][Data.NUMERO].nunique()
        resultat_ins = [Total, tot_year, tot, int(
            (tot_year*100)/Total) if Total > 0 else 0]
        dff = pd.DataFrame({Data.TOTAL: [resultat_ins[0]], Data.REALISE_DANS_L_ANNEE: [
                           resultat_ins[1]], Data.TOTAL_CUMULE: [resultat_ins[2]], Data.POURCENTAGE_INS: [resultat_ins[3]]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Linéaire de réseaux sur parcelles ou voie privée


def LRSPVP(filtered_data, canexp_cadastre_merged, canexp_voie_merged, group_column):
    if group_column:
        # Create copies to avoid SettingWithCopyWarning
        canexp_cadastre_merged = canexp_cadastre_merged.copy()
        canexp_voie_merged = canexp_voie_merged.copy()

        canexp_cadastre_merged['lin_f'] = canexp_cadastre_merged[Data.LONGUEUR] * \
            canexp_cadastre_merged['T_P_hors_Metropole']/100000
        canexp_voie_merged['lin_f'] = canexp_voie_merged[Data.LONGUEUR] * \
            canexp_voie_merged['T_P_hors_Metropole']/100000

        df_cad_grouped = canexp_cadastre_merged.groupby(group_column)
        df_voie_grouped = canexp_voie_merged.groupby(group_column)
        df_niv_grouped = filtered_data[Data.QUERY_CANAEXP].groupby(
            group_column)

        # Add include_groups=False to silence FutureWarning
        resultat_cad = round(df_cad_grouped.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANA_EXP)['lin_f'].sum(), include_groups=False), 3).reset_index()
        resultat_voie = round(df_voie_grouped.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANA_EXP)['lin_f'].sum(), include_groups=False), 3).reset_index()
        resultat_niv = round(df_niv_grouped.apply(lambda x: x.drop_duplicates(subset=Data.ID_CANA_EXP)[
                             Data.LONGUEUR].sum()/1000, include_groups=False), 3).reset_index()

        resultat_cad.columns = [group_column, 'lin_cad']
        resultat_voie.columns = [group_column, 'lin_voie']
        resultat_niv.columns = [group_column, 'lin_niv']

        dff = pd.merge(resultat_cad, resultat_voie,
                       on=group_column, how='outer').reset_index(drop=True)
        dff = pd.merge(dff, resultat_niv, on=group_column,
                       how='outer').reset_index(drop=True)
        dff['lineaire'] = dff['lin_cad'] + dff['lin_voie']
        dff = dff.fillna(0)
        dff['pourcentage'] = round((dff['lineaire'] * 100) / dff['lin_niv'], 2)

        if dff.empty:
            dff = pd.DataFrame({group_column: [None], 'lin_cad': [0], 'lin_voie': [
                               0], 'lineaire': [0], 'pourcentage': [0]})

    else:
        # Create copies to avoid SettingWithCopyWarning
        canexp_cadastre_merged = canexp_cadastre_merged.copy()
        canexp_voie_merged = canexp_voie_merged.copy()

        canexp_cadastre_merged = canexp_cadastre_merged.drop_duplicates(
            subset=Data.ID_CANA_EXP)
        canexp_voie_merged = canexp_voie_merged.drop_duplicates(
            subset=Data.ID_CANA_EXP)
        canexp_cadastre_merged['lin_f'] = canexp_cadastre_merged[Data.LONGUEUR] * \
            canexp_cadastre_merged['T_P_hors_Metropole']/100000
        canexp_voie_merged['lin_f'] = canexp_voie_merged[Data.LONGUEUR] * \
            canexp_voie_merged['T_P_hors_Metropole']/100000

        resultat = round(canexp_cadastre_merged['lin_f'].sum(
        ) + canexp_voie_merged['lin_f'].sum(), 3)
        tot = filtered_data[Data.QUERY_CANAEXP].drop_duplicates(
            subset=Data.ID_CANA_EXP)[Data.LONGUEUR].sum()/1000

        dff = pd.DataFrame({
            'lineaire': [resultat],
            'pourcentage': [round(resultat*100/tot, 2) if tot > 0 else 0]
        })

    if dff.empty:
        # Create proper empty DataFrame structure
        if group_column:
            dff = pd.DataFrame({group_column: [None], 'lin_cad': [0], 'lin_voie': [
                               0], 'lineaire': [0], 'pourcentage': [0]})
        else:
            dff = pd.DataFrame({'lineaire': [0], 'pourcentage': [0]})

    return dff

# Nombre de parcelles privées traversées par les réseaux


def NPPTR(filtered_data, gdf_cad, group_column):
    filtered_data[Data.QUERY_PARCELLES][Data.GEOM] = filtered_data[Data.QUERY_PARCELLES][Data.GEOM].apply(
        convert_geometry)
    filtered_data[Data.QUERY_PARCELLES] = gpd.GeoDataFrame(
        filtered_data[Data.QUERY_PARCELLES], geometry=Data.GEOM, crs='EPSG:3946')
    gdf_cad = gpd.GeoDataFrame(gdf_cad, geometry='geometry', crs='EPSG:3946')

    intersection = gpd.overlay(
        filtered_data[Data.QUERY_PARCELLES], gdf_cad[gdf_cad['T_P_hors_Metropole'] >= 50], how='intersection')
    liste_colonnes = [Data.ID_PARCELLE, 'codenatureproprietaire', 'natureproprietaire', Data.ID_BV_GRAND, Data.ID_STEU, Data.NOM_STEU,
                      Data.ID_COM, Data.TEXTE, 'identifiantcoursdeau', Data.ID_BV_RUISSEAU, 'identifiantcaptage', Data.NOM_CAPTAGE, Data.BASSIN]
    intersection = intersection[liste_colonnes]

    if group_column:
        df_grouped = intersection.groupby(group_column)
        df_niv_grouped = filtered_data[Data.QUERY_PARCELLES].groupby(
            group_column)

        resultat = df_grouped[Data.ID_PARCELLE].nunique().reset_index()
        resultat_niv = df_niv_grouped[Data.ID_PARCELLE].nunique().reset_index()

        resultat.columns = [group_column, 'nbre_parcelle']
        resultat_niv.columns = [group_column, 'nbre_parcelle']
        dff = pd.DataFrame(resultat)

        if dff.empty:
            dff['pourcentage'] = 0
        else:
            dff['pourcentage'] = round((dff['nbre_parcelle']*100) / resultat_niv['nbre_parcelle'],
                                       0) if resultat_niv['nbre_parcelle'].iloc[0] > 0 else 0
    else:
        resultat = intersection[Data.ID_PARCELLE].nunique()
        tot = filtered_data[Data.QUERY_PARCELLES][Data.ID_PARCELLE].nunique()
        dff = pd.DataFrame({'nbre_parcelle': [resultat], 'pourcentage': [
                           round(resultat*100/tot, 2) if tot > 0 else 0]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Valeur patrimoniale à neuf OGEP (Millions €)


def VPOGEP(filtered_data, VP_OGEP, group_column):
    # Create explicit copy to avoid SettingWithCopyWarning
    df_filtererd = filtered_data[Data.QUERY_OGEP][filtered_data[Data.QUERY_OGEP][Data.NATURE_OGEP].isin(
        # {1: Tranchée, 2: Noue, 3: Noue composée, 5: Tranchée Stockholm}
        [1, 2, 3, 5])].copy()

    # Check if Data.LONGUEUR exists in df_filtererd
    if Data.LONGUEUR not in df_filtererd.columns or df_filtererd.empty:
        # Return empty DataFrame with proper structure
        if group_column:
            return pd.DataFrame(columns=[group_column, Indicators.VP_OGEP_COL])
        else:
            return pd.DataFrame(columns=[Indicators.VP_OGEP_COL])

    # Now safely modify the copy
    df_filtererd[Indicators.VALEUR] = df_filtererd[Data.LONGUEUR] * \
        VP_OGEP / 1000

    if group_column:
        df_grouped = df_filtererd.groupby(group_column)
        resultat = round(df_grouped.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_OGEP)[Indicators.VALEUR].sum()), 1).reset_index()
        resultat.columns = [group_column, Indicators.VP_OGEP_COL]
        dff = resultat.copy()  # Use copy() instead of pd.DataFrame(resultat)

    else:
        resultat = round(df_filtererd.drop_duplicates(
            subset=[Data.ID_OGEP])[Indicators.VALEUR].sum(), 1)
        # Create list for proper DataFrame structure
        dff = pd.DataFrame({Indicators.VP_OGEP_COL: [resultat]})

    if dff.empty:
        # Create proper empty DataFrame structure
        if group_column:
            dff = pd.DataFrame(
                {group_column: [None], Indicators.VP_OGEP_COL: [0]})
        else:
            dff = pd.DataFrame({Indicators.VP_OGEP_COL: [0]})

    return dff

# Valeur patrimoniale à neuf Bassins (ENT ET OUV) (Millions €)


def VPBassins(filtered_data, VP_OUV, VP_ENT, group_column):
    # Create explicit copies to avoid SettingWithCopyWarning
    df_OUV = filtered_data[Data.QUERY_BASSINS][filtered_data[Data.QUERY_BASSINS]
                                               [Data.NATURE] == 'OUV'].copy()
    df_ENT = filtered_data[Data.QUERY_BASSINS][filtered_data[Data.QUERY_BASSINS]
                                               [Data.NATURE] == 'ENT'].copy()

    # Now safely modify the copies
    df_OUV[Indicators.VALEUR] = df_OUV['volumeexploitation'] * \
        VP_OUV / 1000000  # (Millions €)
    df_ENT[Indicators.VALEUR] = df_ENT['volumeexploitation'] * \
        VP_ENT / 1000000  # (Millions €)

    if group_column:
        resultat_OUV = pd.DataFrame(columns=[group_column, Indicators.VP_OUV])
        resultat_ENT = pd.DataFrame(columns=[group_column, Indicators.VP_ENT])

        if not (df_OUV[df_OUV[group_column].notna()].empty):
            df_OUV_grouped = df_OUV.groupby(group_column)
            resultat_OUV = (round(df_OUV_grouped.apply(lambda x: x.drop_duplicates(
                subset=Data.ID_BASSIN)[Indicators.VALEUR].sum()), 1)).reset_index()
            resultat_OUV.columns = [group_column, Indicators.VP_OUV]

        if not (df_ENT[df_ENT[group_column].notna()].empty):
            df_ENT_grouped = df_ENT.groupby(group_column)
            resultat_ENT = (round(df_ENT_grouped.apply(lambda x: x.drop_duplicates(
                subset=Data.ID_BASSIN)[Indicators.VALEUR].sum()), 1)).reset_index()
            resultat_ENT.columns = [group_column, Indicators.VP_ENT]

        if (not resultat_OUV.empty) and (not resultat_ENT.empty):
            dff = pd.merge(resultat_OUV, resultat_ENT,
                           on=group_column, how='outer')
            dff[Indicators.VP_TOT] = dff[Indicators.VP_OUV] + \
                dff[Indicators.VP_ENT]
        elif not resultat_OUV.empty:
            dff = resultat_OUV.copy()
            dff[Indicators.VP_ENT] = 0
            dff[Indicators.VP_TOT] = dff[Indicators.VP_OUV]
        elif not resultat_ENT.empty:
            dff = resultat_ENT.copy()
            dff[Indicators.VP_OUV] = 0
            dff[Indicators.VP_TOT] = dff[Indicators.VP_ENT]
        else:
            dff = pd.DataFrame(
                columns=[group_column, Indicators.VP_OUV, Indicators.VP_ENT, Indicators.VP_TOT])

    else:
        resultat = [
            round(df_OUV.drop_duplicates(subset=[Data.ID_BASSIN])[
                  Indicators.VALEUR].sum(), 1),
            round(df_ENT.drop_duplicates(subset=[Data.ID_BASSIN])[
                  Indicators.VALEUR].sum(), 1),
            round(((df_OUV.drop_duplicates(subset=[Data.ID_BASSIN])[Indicators.VALEUR].sum(
            )) + (df_ENT.drop_duplicates(subset=[Data.ID_BASSIN])[Indicators.VALEUR].sum())), 1)
        ]
        dff = pd.DataFrame({Indicators.VP_OUV: [resultat[0]], Indicators.VP_ENT: [
                           resultat[1]], Indicators.VP_TOT: [resultat[2]]})

    if dff.empty:
        # Create a proper empty row with zeros
        if group_column:
            dff = pd.DataFrame({group_column: [None], Indicators.VP_OUV: [
                               0], Indicators.VP_ENT: [0], Indicators.VP_TOT: [0]})
        else:
            dff = pd.DataFrame({Indicators.VP_OUV: [0], Indicators.VP_ENT: [
                               0], Indicators.VP_TOT: [0]})

    return dff

# Valeur patrimoniale à neuf STR (Millions €)


def VPSTR(filtered_data, VP_STR, group_column):
    if group_column:
        # Liste de tous les groupes possibles
        all_groups = (
            filtered_data[Data.QUERY_CANAP][group_column]
            .drop_duplicates()
            .to_frame()
        )

        # Calcul uniquement sur les données STARE
        df = filtered_data[Data.QUERY_STARE].copy()
        grp = (df.groupby(group_column)[Data.ID_STARE]
                 .nunique()
                 .mul(VP_STR)
                 .round(1)
                 .reset_index(name=Indicators.VP_STR_COL))

        # Fusion pour conserver aussi les groupes sans STR
        dff = (all_groups
               .merge(grp, on=group_column, how='left')
               .fillna({Indicators.VP_STR_COL: 0.0}))

    else:
        total = round(filtered_data[Data.QUERY_STARE]
                      [Data.ID_STARE].nunique() * VP_STR, 1)
        dff = pd.DataFrame({Indicators.VP_STR_COL: [total]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


# Valeur patrimoniale à neuf STEU (MD€)
def VPSTEU(filtered_data, VP_STEU, group_column):
    # copie + calcul propre de la valeur (en M€)
    df = filtered_data[Data.QUERY_STEU].copy()
    df['__cap'] = df.get('capacite', 0).fillna(0)
    df['__val'] = (df['__cap'] * VP_STEU) / 1_000_000  # M€

    # on compte chaque STEU une seule fois
    df = df.drop_duplicates(subset=Data.ID_STEU)

    if group_column:
        # liste complète des groupes (ex. toutes les communes)
        all_groups = (
            filtered_data[Data.QUERY_CANAP][group_column]
            .drop_duplicates()
            .to_frame()
        )

        # somme par groupe
        grp = (df.groupby(group_column)['__val']
                 .sum()
                 .round(1)
                 .reset_index(name=Indicators.VP_STEU_COL))

        # left join pour garder aussi les groupes sans STEU
        dff = (all_groups
               .merge(grp, on=group_column, how='left')
               .fillna({Indicators.VP_STEU_COL: 0.0}))
    else:
        total = round(df['__val'].sum(), 1)
        dff = pd.DataFrame({Indicators.VP_STEU_COL: [total]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


# Valeur patrimoniale à neuf FPR (K€)
def VPFPR(filtered_data, VP_FPR, group_column):
    df_filtered = filtered_data[Data.QUERY_STEU][
        filtered_data[Data.QUERY_STEU][Data.NOM_STEU].str.contains(
            "Filtre planté de roseaux", na=False)
    ].copy()

    if group_column:
        # Liste de tous les groupes possibles
        all_groups = (
            filtered_data[Data.QUERY_CANAP][group_column]
            .drop_duplicates()
            .to_frame()
        )

        # Calcul sur les FPR uniquement
        grp = (
            df_filtered.groupby(group_column)[Data.ID_STEU]
            .nunique()
            .mul(VP_FPR)
            .reset_index(name=Indicators.VP_FPR_COL)
        )

        # Fusion pour inclure les groupes sans FPR
        dff = (
            all_groups
            .merge(grp, on=group_column, how='left')
            .fillna({Indicators.VP_FPR_COL: 0})
        )

    else:
        resultat = int(df_filtered[Data.ID_STEU].nunique() * VP_FPR)
        dff = pd.DataFrame({Indicators.VP_FPR_COL: [resultat]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


# Valeur patrimoniale à neuf Trémies (Millions €)
def VPTREM(filtered_data, VP_TREM, group_column):
    if group_column:
        df_grouped = filtered_data[Data.QUERY_TREMIE].groupby(group_column)
        resultat = (
            round(df_grouped[Data.ID_TREMIE].nunique() * VP_TREM, 1)).reset_index()
        resultat.columns = [group_column, Indicators.VP_TREM_COL]
        dff = pd.DataFrame(resultat)

    else:
        resultat = round(
            filtered_data[Data.QUERY_TREMIE][Data.ID_TREMIE].nunique() * VP_TREM, 1)
        dff = pd.DataFrame({Indicators.VP_TREM_COL: resultat}, index=[0])

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Nombre de bassins (ENT et OUV) récolés


def NBR(dfRecBas, group_column):

    if 'Recolement' not in dfRecBas or dfRecBas.empty:
        # Return empty DataFrame with proper structure
        if group_column:
            return pd.DataFrame(columns=[group_column])
        else:
            return pd.DataFrame()

    dfRecBas_bis = dfRecBas[dfRecBas['Recolement'] == 'O']

    if group_column:
        df_rec_grouped = dfRecBas_bis.groupby(group_column)
        df_tot_grouped = dfRecBas.groupby(group_column)

        resultat_rec = df_rec_grouped[Data.ID_BASSIN].nunique().reset_index()
        resultat_tot = df_tot_grouped[Data.ID_BASSIN].nunique().reset_index()

        resultat_rec.columns = [group_column, Indicators.NBRE_REC]
        resultat_tot.columns = [group_column, Indicators.NBRE_TOT]
        dff = pd.merge(resultat_rec, resultat_tot,
                       on=group_column, how='outer').reset_index()

        if not (dff.empty):
            dff[Indicators.POURCENTAGE] = round(
                (dff[Indicators.NBRE_REC]*100) / dff[Indicators.NBRE_TOT]) if dff[Indicators.NBRE_TOT].iloc[0] > 0 else 0
        else:
            dff[Indicators.POURCENTAGE] = 0
        dff = dff.fillna(0)
    else:
        resultat = dfRecBas_bis[Data.ID_BASSIN].nunique()
        total_bassins = dfRecBas[Data.ID_BASSIN].nunique()
        dff = pd.DataFrame({Indicators.NBRE_REC: [resultat], Indicators.NBRE_TOT: [total_bassins], Indicators.POURCENTAGE: [
                           int(round(resultat*100/total_bassins)) if total_bassins > 0 else 0]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
        return dff
    else:
        return dff

# Linéaire de linéaire d'infiltration inspecté dans l'année


def LLI(filtered_data, group_column):
    """FONCTION FAUSSE TODO
    Ne sors pas les linéaires d'infiltrations inspecté dans l'année mais ceux installés...
    Comme pour la sauvegarde du socle on est sur pub et pas sur ref, on n'a plus le champs datecreation
    Je propose donc qu'on mette en standby cette fonction en attendant de trouver un moyen de sortir les inspectés..."""

    return None

    filtered_data[Data.QUERY_DRAIN][Data.GEOM] = filtered_data[Data.QUERY_DRAIN][Data.GEOM].apply(
        convert_geometry)
    gdf_drain = gpd.GeoDataFrame(
        filtered_data[Data.QUERY_DRAIN], geometry=Data.GEOM)
    gdf_drain[Data.LONGUEUR] = gdf_drain[Data.GEOM].length
    gdf_drain['datecreation'] = pd.to_datetime(gdf_drain['datecreation'])
    gdf_drain['annee'] = gdf_drain['datecreation'].dt.year

    current_year = datetime.now().year
    if group_column:
        df_LLI = gdf_drain[gdf_drain['annee'] ==
                           current_year][group_column].dropna()
        if df_LLI.empty:
            dff = pd.DataFrame(
                columns=[Data.LONGUEUR, 'longueur_cum', Indicators.POURCENTAGE])
            dff.loc[0] = [0] * len(dff.columns)
            return (dff)
        else:
            gdf_grouped = gdf_drain[gdf_drain['annee']
                                    == current_year].groupby(group_column)
            gdf_tot_grouped = gdf_drain.groupby(group_column)
            resultat_grp = round(gdf_grouped.apply(lambda x: x.drop_duplicates(
                subset='iddrain')[Data.LONGUEUR].sum()/1000), 3).reset_index()
            resultat_tot = round(gdf_tot_grouped.apply(lambda x: x.drop_duplicates(
                subset='iddrain')[Data.LONGUEUR].sum()/1000), 3).reset_index()
            resultat_grp.columns = [group_column, Data.LONGUEUR]
            resultat_tot.columns = [group_column, 'longueur_cum']
            # Fusionner les résultats
            dff = pd.merge(resultat_grp, resultat_tot, on=group_column)
            dff = dff.fillna(0)

            if not (dff.empty):
                dff[Indicators.POURCENTAGE] = round(
                    (dff[Data.LONGUEUR]*100) / dff['longueur_cum'])
            else:
                dff[Indicators.POURCENTAGE] = 0
    else:
        gdf_sans_doublons = gdf_drain.drop_duplicates(subset=['iddrain'])
        current_data = gdf_sans_doublons[gdf_sans_doublons['annee'] == current_year].copy(
        )
        resultat = current_data[Data.LONGUEUR].sum() / 1000
        dff = pd.DataFrame({Data.LONGUEUR: [round(resultat, 1)], 'longueur_cum': [int(gdf_sans_doublons[Data.LONGUEUR].sum(
        ) / 1000)], Indicators.POURCENTAGE: [int((resultat * 100000) / gdf_sans_doublons[Data.LONGUEUR].sum())]})
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return (dff)

# Nombre de STR récolés


def NSR(dfRecSTR, group_column):

    if Data.RECOLEMENT not in dfRecSTR or dfRecSTR.empty:
        # Return empty DataFrame with proper structure
        if group_column:
            return pd.DataFrame(columns=[group_column])
        else:
            return pd.DataFrame()

    dfRecSTR_bis = dfRecSTR[dfRecSTR[Data.RECOLEMENT] == Data.OUI]

    if group_column:
        # Base de toutes les communes présentes dans ce DF (référence d'affichage)
        base = dfRecSTR[[group_column]].drop_duplicates()

        # Comptages
        resultat_rec = (
            dfRecSTR_bis.groupby(group_column)[Data.ID_STARE]
            .nunique()
            .reset_index(name='nbre_rec')
        )
        resultat_tot = (
            dfRecSTR.groupby(group_column)[Data.ID_STARE]
            .nunique()
            .reset_index(name='nbre_tot')
        )

        # Left-join sur la base pour garder toutes les communes, puis complétion à 0
        dff = (
            base.merge(resultat_rec, on=group_column, how='left')
                .merge(resultat_tot, on=group_column, how='left')
                .fillna({'nbre_rec': 0, 'nbre_tot': 0})
        )

        # Types + pourcentage
        dff['nbre_rec'] = dff['nbre_rec'].astype(int)
        dff['nbre_tot'] = dff['nbre_tot'].astype(int)
        dff['pourcentage'] = 0.0
        mask = dff['nbre_tot'] > 0
        dff.loc[mask, 'pourcentage'] = (
            dff.loc[mask, 'nbre_rec'] * 100.0 / dff.loc[mask, 'nbre_tot']
        ).round(2)

    else:
        n_rec = dfRecSTR_bis[Data.ID_STARE].nunique()
        n_tot = dfRecSTR[Data.ID_STARE].nunique()
        dff = pd.DataFrame({
            'nbre_rec': [n_rec],
            'nbre_tot': [n_tot],
            'pourcentage': [round(n_rec * 100.0 / n_tot, 2) if n_tot > 0 else 0.0]
        })

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


def NDOR(filtered_data, group_column):
    filtered_data[Data.QUERY_DO] = filtered_data[Data.QUERY_DO].fillna(False)
    filtered_data_bis = filtered_data[Data.QUERY_DO][filtered_data[Data.QUERY_DO][Data.RECOLEMENT]]

    if group_column:
        df_rec_grouped = filtered_data_bis.groupby(group_column)
        df_tot_grouped = filtered_data[Data.QUERY_DO].groupby(group_column)

        resultat_rec = df_rec_grouped[Data.ID_DEVORAGE].nunique().reset_index()
        resultat_tot = df_tot_grouped[Data.ID_DEVORAGE].nunique().reset_index()

        resultat_rec.columns = [group_column, Indicators.NBRE_REC]
        resultat_tot.columns = [group_column, Indicators.NBRE_TOT]
        dff = pd.merge(resultat_rec, resultat_tot,
                       on=group_column, how='outer').reset_index()
        dff = dff.fillna(0)

        if not (dff.empty):
            dff[Indicators.POURCENTAGE] = round(
                (dff[Indicators.NBRE_REC]*100) / dff[Indicators.NBRE_TOT], 2) if dff[Indicators.NBRE_TOT].iloc[0] > 0 else 0
        else:
            dff[Indicators.POURCENTAGE] = 0
    else:
        resultat = filtered_data_bis[Data.ID_DEVORAGE].nunique()
        total_do = filtered_data[Data.QUERY_4][Data.ID_DEVORAGE].nunique()
        dff = pd.DataFrame({Indicators.NBRE_REC: [resultat], Indicators.NBRE_TOT: [
                           total_do], Indicators.POURCENTAGE: [round(resultat*100/total_do, 2) if total_do > 0 else 0]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
        return dff
    else:
        return dff


def NDesR(filtered_data, group_column):
    filtered_data[Data.QUERY_TRAITEMENT] = filtered_data[Data.QUERY_TRAITEMENT].fillna(
        False)
    filtered_data[Data.QUERY_TRAITEMENT] = filtered_data[Data.QUERY_TRAITEMENT][filtered_data[Data.QUERY_TRAITEMENT]
                                                                                [Data.TYPE_TRAITEMENT] == Data.SAB]

    if Data.RECOLEMENT not in filtered_data[Data.QUERY_TRAITEMENT] or filtered_data[Data.QUERY_TRAITEMENT].empty:
        # Return empty DataFrame with proper structure
        if group_column:
            return pd.DataFrame(columns=[group_column])
        else:
            return pd.DataFrame()

    filtered_data_bis = filtered_data[Data.QUERY_TRAITEMENT][filtered_data[Data.QUERY_TRAITEMENT][Data.RECOLEMENT]]

    if group_column:
        df_rec_grouped = filtered_data_bis.groupby(group_column)
        df_tot_grouped = filtered_data[Data.QUERY_TRAITEMENT].groupby(
            group_column)

        resultat_rec = df_rec_grouped[Data.ID_TRAITEMENT].nunique(
        ).reset_index()
        resultat_tot = df_tot_grouped[Data.ID_TRAITEMENT].nunique(
        ).reset_index()

        resultat_rec.columns = [group_column, Indicators.NBRE_REC]
        resultat_tot.columns = [group_column, Indicators.NBRE_TOT]
        dff = pd.merge(resultat_rec, resultat_tot,
                       on=group_column, how='outer').reset_index()
        dff = dff.fillna(0)

        if not (dff.empty):
            dff[Indicators.POURCENTAGE] = round(
                (dff[Indicators.NBRE_REC]*100) / dff[Indicators.NBRE_TOT], 2) if dff[Indicators.NBRE_TOT].iloc[0] > 0 else 0
        else:
            dff[Indicators.POURCENTAGE] = 0
    else:
        resultat = filtered_data_bis[Data.ID_TRAITEMENT].nunique()
        total_des = filtered_data[Data.QUERY_TRAITEMENT][Data.ID_TRAITEMENT].nunique(
        )
        dff = pd.DataFrame({Indicators.NBRE_REC: [resultat], Indicators.NBRE_TOT: [
                           total_des], Indicators.POURCENTAGE: [round(resultat*100/total_des, 2) if total_des > 0 else 0]})

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
        return dff
    else:
        return dff

# Nombre de Tremies récolés


def NTR(filtered_data, group_column):
    """
    Calcule le nombre et le pourcentage de trémies récolées.
    """
    dfRecTRM = filtered_data
    dfRecTRM_bis = dfRecTRM[dfRecTRM[Data.RECOLEMENT] == Data.OUI]

    # --- Cas 1 : Calcul par groupe ---
    if group_column:
        df_rec_grouped = dfRecTRM_bis.groupby(group_column)
        df_tot_grouped = dfRecTRM.groupby(group_column)

        resultat_rec = df_rec_grouped[Data.ID_TREMIE].nunique().reset_index()
        resultat_tot = df_tot_grouped[Data.ID_TREMIE].nunique().reset_index()

        resultat_rec.columns = [group_column, Indicators.NBRE_REC]
        resultat_tot.columns = [group_column, Indicators.NBRE_TOT]

        dff = pd.merge(resultat_rec, resultat_tot,
                       on=group_column, how='outer')
        # On supprime la colonne 'index' inutile ajoutée par le reset_index() précédent
        if 'index' in dff.columns:
            dff = dff.drop(columns=['index'])
        dff = dff.fillna(0)

        # **LA CORRECTION EST ICI**
        if not dff.empty:
            # Initialiser la colonne avec une valeur par défaut
            dff[Indicators.POURCENTAGE] = 0

            # Créer un masque pour les lignes où le total est non nul
            non_zero_mask = dff[Indicators.NBRE_TOT] > 0

            # Calculer le pourcentage uniquement sur ces lignes
            percentage_series = (dff.loc[non_zero_mask, Indicators.NBRE_REC]
                                 * 100) / dff.loc[non_zero_mask, Indicators.NBRE_TOT]

            # Assigner le résultat et convertir en entier
            dff.loc[non_zero_mask, Indicators.POURCENTAGE] = round(
                percentage_series).astype(int)
        else:
            # Si le dataframe est vide après la fusion, on s'assure qu'il a la bonne colonne
            dff[Indicators.POURCENTAGE] = 0

    # --- Cas 2 : Calcul global ---
    else:
        resultat = dfRecTRM_bis[Data.ID_TREMIE].nunique()
        total_tremies = dfRecTRM[Data.ID_TREMIE].nunique()

        pourcentage = 0
        if total_tremies > 0:
            pourcentage = int(round(resultat * 100 / total_tremies))

        dff = pd.DataFrame({
            Indicators.NBRE_REC: [resultat],
            Indicators.NBRE_TOT: [total_tremies],
            Indicators.POURCENTAGE: [pourcentage]
        })

    return dff

# Nombre de FPR récolés


def NFR(filtered_data, dossier_FPR, group_column):
    # --- Recherche des dossiers contenant un sous-dossier "plan" non vide ---
    dossier_trouve = []
    for dossier_parent, sous_dossiers, _ in os.walk(dossier_FPR):
        for sous_dossier in sous_dossiers:
            if sous_dossier == "plan":
                chemin_plan = os.path.join(dossier_parent, sous_dossier)
                if os.path.isdir(chemin_plan) and os.listdir(chemin_plan):
                    nom_dossier = os.path.basename(dossier_parent)
                    dossier_trouve.append(nom_dossier)

    # --- Sélection des FPR dans les données STEU ---
    df_fpr = filtered_data[Data.QUERY_STEU].copy()
    df_fpr = df_fpr[df_fpr[Data.NOM_STEU].str.contains(
        "Filtre planté de roseaux", na=False)]

    # --- Vérification de présence d’un recolement ---
    df_fpr[Data.RECOLEMENT] = df_fpr[Data.NOM_STEU].apply(
        lambda nom: Data.OUI if any(
            nom in dossier for dossier in dossier_trouve) else Data.NON
    )

    df_fpr_rec = df_fpr[df_fpr[Data.RECOLEMENT] == Data.OUI]

    # --- Traitement groupé (par commune, bassin, etc.) ---
    if group_column:
        total_group = df_fpr.groupby(group_column)[Data.ID_STEU].nunique(
        ).reset_index(name=Indicators.NBRE_TOT)
        rec_group = df_fpr_rec.groupby(group_column)[
            Data.ID_STEU].nunique().reset_index(name=Indicators.NBRE_REC)

        dff = pd.merge(total_group, rec_group,
                       on=group_column, how='left').fillna(0)

        dff[Indicators.POURCENTAGE] = dff.apply(
            lambda row: round((row[Indicators.NBRE_REC] * 100) /
                              row[Indicators.NBRE_TOT], 2) if row[Indicators.NBRE_TOT] > 0 else 0,
            axis=1
        )

    # --- Vision globale (Zoom Métropole) ---
    else:
        total = df_fpr[Data.ID_STEU].nunique()
        rec = df_fpr_rec[Data.ID_STEU].nunique()
        pourcentage = round((rec * 100) / total, 2) if total > 0 else 0

        dff = pd.DataFrame({
            Indicators.NBRE_TOT: [total],
            Indicators.NBRE_REC: [rec],
            Indicators.POURCENTAGE: [pourcentage]
        })

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


# Nombre de  Arbres de pluie récolés
def NAPR(Rec_AP, group_column):
    """
    Calcule le nombre et le pourcentage d'arbres de pluie récolés.
    """
    Rec_AP_bis = Rec_AP[Rec_AP['Ouvrage récolé'] == 'oui']

    # --- Cas 1 : Calcul par groupe ---
    if group_column:
        df_rec_grouped = Rec_AP_bis.groupby(group_column)
        df_tot_grouped = Rec_AP.groupby(group_column)

        resultat_rec = df_rec_grouped[Data.ID_OGEP].nunique().reset_index()
        resultat_tot = df_tot_grouped[Data.ID_OGEP].nunique().reset_index()

        resultat_rec.columns = [group_column, Indicators.NBRE_REC]
        resultat_tot.columns = [group_column, Indicators.NBRE_TOT]

        dff = pd.merge(resultat_rec, resultat_tot, on=group_column,
                       how='outer').reset_index(drop=True)
        dff = dff.fillna(0)

        if dff.empty:
            dff[Indicators.POURCENTAGE] = 0
        else:
            # S'assurer que le dénominateur n'est pas zéro avant la division
            # La division par zéro crée des 'inf' que .astype(int) ne peut pas gérer
            dff[Indicators.POURCENTAGE] = 0  # Initialiser la colonne
            non_zero_mask = dff[Indicators.NBRE_TOT] != 0

            # **LA CORRECTION EST ICI**
            # On calcule le pourcentage uniquement pour les lignes où le total n'est pas nul
            percentage_series = (dff.loc[non_zero_mask, Indicators.NBRE_REC]
                                 * 100) / dff.loc[non_zero_mask, Indicators.NBRE_TOT]
            dff.loc[non_zero_mask, Indicators.POURCENTAGE] = round(
                percentage_series).astype(int)

    # --- Cas 2 : Calcul global ---
    else:
        resultat = Rec_AP_bis[Data.ID_OGEP].nunique()
        # Dénominateur corrigé pour être cohérent
        total = Rec_AP[Data.ID_OGEP].nunique()

        pourcentage = 0
        if total > 0:
            pourcentage = int(round(resultat * 100 / total))

        dff = pd.DataFrame({
            Indicators.NBRE_REC: [resultat],
            Indicators.NBRE_TOT: [total],
            Indicators.POURCENTAGE: [pourcentage]
        })

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff

# Linéaire total d'idées de faire travaux Réseaux


def LRIT(df_idees_res, group_column):
    if group_column:
        df_grouped = df_idees_res.groupby(group_column)
        resultat = (round(df_grouped.apply(lambda x: x.drop_duplicates(subset=Data.ID_CANA_EXP)[
                    Data.LONGUEUR].sum() / 1000))).reset_index(name=Indicators.LONG_IDEE)
        dff = pd.DataFrame(resultat)

    else:
        resultat = [int(round(df_idees_res.drop_duplicates(
            subset=[Data.ID_CANA_EXP])[Data.LONGUEUR].sum() / 1000))]
        dff = pd.DataFrame({Indicators.LONG_IDEE: resultat})
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return dff

# Age de réseaux


def AR(filtered_data, group_column):
    year = datetime.now().year
    df_ages = filtered_data[Data.QUERY_CANAP].copy()

    condition1 = df_ages[Data.ANNEE_POSE].isnull(
    ) & df_ages[Data.ANNEE_POSE_SUP].notna() & df_ages[Data.ANNEE_POSE_INF].notna()
    condition2 = df_ages[Data.ANNEE_POSE].isnull(
    ) & df_ages[Data.ANNEE_POSE_SUP].isnull() & df_ages[Data.ANNEE_POSE_INF].notna()
    condition3 = df_ages[Data.ANNEE_POSE].isnull(
    ) & df_ages[Data.ANNEE_POSE_SUP].notna() & df_ages[Data.ANNEE_POSE_INF].isnull()

    df_ages.loc[condition1, Data.ANNEE_POSE] = df_ages.loc[condition1].apply(
        lambda row: np.mean([row[Data.ANNEE_POSE_SUP], row[Data.ANNEE_POSE_INF]]), axis=1)
    df_ages.loc[condition2,
                Data.ANNEE_POSE] = df_ages.loc[condition2, Data.ANNEE_POSE_INF]
    df_ages.loc[condition3,
                Data.ANNEE_POSE] = df_ages.loc[condition3, Data.ANNEE_POSE_SUP]

    df_ages = df_ages.dropna(subset=[Data.ANNEE_POSE])
    df_ages = df_ages[df_ages[Data.ANNEE_POSE].astype(int) != 0]
    df_ages['age'] = year - df_ages[Data.ANNEE_POSE].astype(int)

    bornes = [0, 25, 50, 75, float('inf')]
    labels = [Data.AGE_0_25, Data.AGE_26_50, Data.AGE_51_75, Data.AGE_OVER_75]
    df_ages['tranche_age'] = pd.cut(df_ages['age'], bins=bornes, labels=labels)

    if group_column:
        # Add observed=False to maintain current behavior and silence FutureWarning
        groupes = df_ages.groupby(
            [group_column, 'tranche_age'], observed=False)
        # Add include_groups=False to silence the apply FutureWarning
        indicateur_sum = round(groupes.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, include_groups=False), 3)
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column,
                             'tranche_age', Indicators.LONGUEUR_SUM]
        dff = resultats.copy()  # Use copy() instead of pd.DataFrame(resultats)

    else:
        # Add observed=False to maintain current behavior and silence FutureWarning
        groupes = df_ages.groupby('tranche_age', observed=False)
        # Add include_groups=False to silence the apply FutureWarning
        indicateur_sum = round(groupes.apply(lambda x: x.drop_duplicates(
            subset=Data.ID_CANAP)[Data.LONGUEUR].sum()/1000, include_groups=False), 3)
        resultats = indicateur_sum.reset_index()
        resultats.columns = ['tranche_age', Indicators.LONGUEUR_SUM]
        dff = resultats.copy()  # Use copy() instead of pd.DataFrame(resultats)

    if dff.empty:
        # Create proper empty DataFrame structure
        if group_column:
            dff = pd.DataFrame({group_column: [None], 'tranche_age': [
                               None], 'longueur_sum': [0]})
        else:
            dff = pd.DataFrame({'tranche_age': [None], 'longueur_sum': [0]})
            # --- Bloc pour transformer en une seule ligne par commune ---
    if group_column:
        dff_pivot = dff.pivot(
            index=group_column, columns='tranche_age', values=Indicators.LONGUEUR_SUM)
        dff_pivot = dff_pivot.fillna(0).round(3)

        # Calcul du total
        dff_pivot["Total"] = dff_pivot.sum(axis=1).round(3)

        # Remettre l’index en colonne
        dff = dff_pivot.reset_index()

    return dff

# Nombre de Noues (simples et composées)


def NNo(filtered_data, group_column):
    df_bis = filtered_data[filtered_data[Data.NATURE_OGEP].isin([2, 3])].copy()
    if group_column:
        groupes = df_bis.groupby(group_column)
        indicateur_sum = groupes[Data.ID_OGEP].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, 'NBR_No']
        dff = pd.DataFrame(resultats)

    else:
        resultats_list = [df_bis[Data.ID_OGEP].nunique()]
        dff = pd.DataFrame(resultats_list, columns=['NBR_No'])
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return (dff)

# Nombre de Tranchée (+ tranchée de stockholm)


def NTr(filtered_data, group_column):
    df_bis = filtered_data[filtered_data[Data.NATURE_OGEP].isin([1, 5])].copy()
    if group_column:
        groupes = df_bis.groupby(group_column)
        indicateur_sum = groupes[Data.ID_OGEP].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, 'NBR_Tr']
        dff = pd.DataFrame(resultats)

    else:
        resultats_list = [df_bis[Data.ID_OGEP].nunique()]
        dff = pd.DataFrame(resultats_list, columns=['NBR_Tr'])
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return (dff)

# Nombre de Linéaires d'infiltaration


def NLi(filtered_data, group_column):
    df_bis = filtered_data[filtered_data[Data.NATURE_OGEP].isin(
        [1, 2, 3, 5])].copy()
    if group_column:
        groupes = df_bis.groupby(group_column)
        indicateur_sum = groupes[Data.ID_OGEP].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, 'NBR_Li']
        dff = pd.DataFrame(resultats)

    else:
        resultats_list = [df_bis[Data.ID_OGEP].nunique()]
        dff = pd.DataFrame(resultats_list, columns=['NBR_Li'])
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
    return (dff)

    # Age STEU


def AgeSTEU(filtered_data, group_column):
    """
    Calcule la répartition par âge des STEU.
    - Si group_column est fourni : 1 ligne par commune, colonnes = tranches d'âge (0 si absence).
    - Sinon : répartition globale par tranche d'âge.
    """
    year = datetime.now().year

    # Préparation des données
    df_ages = filtered_data[Data.QUERY_STEU].dropna(
        subset=[Data.ANNEE_CONSTRUCTION]).copy()
    df_ages = df_ages[df_ages[Data.ANNEE_CONSTRUCTION].astype(int) != 0]
    df_ages['age'] = year - df_ages[Data.ANNEE_CONSTRUCTION].astype(int)

    # Tranches d'âge
    bornes = [0, 10, 20, 30, float('inf')]
    labels = [Data.AGE_0_10, Data.AGE_11_20, Data.AGE_21_30, Data.AGE_OVER_30]
    df_ages['tranche_age'] = pd.cut(
        df_ages['age'], bins=bornes, labels=labels, right=False)

    # Calcul par groupe ou global
    if group_column:
        # Comptage par (commune, tranche)
        groupes = df_ages.groupby([group_column, 'tranche_age'])
        indicateur_sum = groupes[Data.ID_STEU].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, 'tranche_age', 'nb_steu']
        dff = pd.DataFrame(resultats)

        # Pivot -> 1 ligne par commune, colonnes = tranches
        dff_pivot = dff.pivot(
            index=group_column, columns='tranche_age', values='nb_steu').fillna(0)

        # S'assurer que toutes les colonnes de tranches existent
        for lab in labels:
            if lab not in dff_pivot.columns:
                dff_pivot[lab] = 0

        # Inclure toutes les communes (même sans STEU)
        base = filtered_data[Data.QUERY_CANAP][group_column].drop_duplicates(
        ).to_frame()
        dff_pivot = base.merge(dff_pivot.reset_index(),
                               on=group_column, how='left').fillna(0)

        # Ordonner les colonnes : commune + tranches
        dff_pivot = dff_pivot[[group_column] + labels]

        # Types propres
        for lab in labels:
            dff_pivot[lab] = dff_pivot[lab].astype(int)

        dff = dff_pivot

    else:
        groupes = df_ages.groupby('tranche_age', observed=True)
        indicateur_sum = groupes[Data.ID_STEU].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = ['tranche_age', 'nb_steu']
        dff = pd.DataFrame(resultats)

    # Gestion des cas vides
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


def AgeSTR(filtered_data, group_column):
    """
    Calcule la répartition par âge des STR selon le type de réseau.
    - Si group_column est fourni : 1 ligne par commune, colonnes = tranches d'âge (0 si absence).
    - Sinon : répartition globale par tranche d'âge.
    """
    year = datetime.now().year

    # Filtrage des données valides
    df_ages = (
        filtered_data[Data.QUERY_STARE]
        [filtered_data[Data.QUERY_STARE][Data.NUMERO].notna() & (
            filtered_data[Data.QUERY_STARE][Data.NUMERO] != 0)]
        .copy()
    )
    df_ages = df_ages.dropna(subset=[Data.ANNEE_CONSTRUCTION])
    df_ages = df_ages[df_ages[Data.ANNEE_CONSTRUCTION].astype(int) != 0]
    df_ages['age'] = year - df_ages[Data.ANNEE_CONSTRUCTION].astype(int)

    # Tranches d'âge
    bornes = [0, 10, 20, 30, float('inf')]
    labels = ['0-10 ans', '11-20 ans', '21-30 ans', '> 30 ans']
    df_ages['tranche_age'] = pd.cut(
        df_ages['age'], bins=bornes, labels=labels, right=False)

    # Agrégation
    if group_column:
        # Comptage par (commune, tranche)
        groupes = df_ages.groupby([group_column, 'tranche_age'])
        indicateur_sum = groupes[Data.NUMERO].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, 'tranche_age', 'nb_str']
        dff = pd.DataFrame(resultats)

        # Pivot -> 1 ligne par commune, colonnes = tranches
        dff_pivot = dff.pivot(index=group_column,
                              columns='tranche_age', values='nb_str').fillna(0)

        # S’assurer que toutes les colonnes de tranches existent
        for lab in labels:
            if lab not in dff_pivot.columns:
                dff_pivot[lab] = 0

        # Inclure toutes les communes (même celles sans STR)
        base = filtered_data[Data.QUERY_CANAP][group_column].drop_duplicates(
        ).to_frame()
        dff_pivot = base.merge(dff_pivot.reset_index(),
                               on=group_column, how='left').fillna(0)

        # Ordonner les colonnes
        dff_pivot = dff_pivot[[group_column] + labels]

        # Conversion en int
        for lab in labels:
            dff_pivot[lab] = dff_pivot[lab].astype(int)

        dff = dff_pivot

    else:
        groupes = df_ages.groupby('tranche_age', observed=True)
        indicateur_sum = groupes[Data.NUMERO].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = ['tranche_age', 'nb_str']
        dff = pd.DataFrame(resultats)

    # Cas vide
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


def AgeSTR_EP(filtered_data, group_column):
    """
    Calcule la répartition par âge des trémies (STR sur réseau EP).
    - Avec group_column : 1 ligne par commune, colonnes = tranches d'âge (0 si absence).
    - Sans group_column : répartition globale par tranche d'âge.
    """
    year = datetime.now().year

    # Données valides
    df_ages = filtered_data[Data.QUERY_TREMIE].dropna(
        subset=[Data.ANNEE_CONSTRUCTION]).copy()
    df_ages = df_ages[df_ages[Data.ANNEE_CONSTRUCTION].astype(int) != 0]
    df_ages['age'] = year - df_ages[Data.ANNEE_CONSTRUCTION].astype(int)

    # Tranches d'âge
    bornes = [0, 10, 20, 30, float('inf')]
    labels = [Data.AGE_0_10, Data.AGE_11_20, Data.AGE_21_30, Data.AGE_OVER_30]
    df_ages['tranche_age'] = pd.cut(
        df_ages['age'], bins=bornes, labels=labels, right=False)

    if group_column:
        # Comptage par (commune, tranche)
        groupes = df_ages.groupby([group_column, 'tranche_age'])
        indicateur_sum = groupes[Data.ID_TREMIE].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = [group_column, 'tranche_age', 'nb_str_ep']
        dff = pd.DataFrame(resultats)

        # Pivot -> 1 ligne par commune, colonnes = tranches
        dff_pivot = dff.pivot(
            index=group_column, columns='tranche_age', values='nb_str_ep').fillna(0)

        # S'assurer que toutes les tranches existent
        for lab in labels:
            if lab not in dff_pivot.columns:
                dff_pivot[lab] = 0

        # Inclure toutes les communes (référentiel complet)
        base = filtered_data[Data.QUERY_CANAP][group_column].drop_duplicates(
        ).to_frame()
        dff_pivot = base.merge(dff_pivot.reset_index(),
                               on=group_column, how='left').fillna(0)

        # Ordonner colonnes et caster en int
        dff_pivot = dff_pivot[[group_column] + labels]
        for lab in labels:
            dff_pivot[lab] = dff_pivot[lab].astype(int)

        dff = dff_pivot

    else:
        groupes = df_ages.groupby('tranche_age', observed=True)
        indicateur_sum = groupes[Data.ID_TREMIE].nunique()
        resultats = indicateur_sum.reset_index()
        resultats.columns = ['tranche_age', 'nb_str_ep']
        dff = pd.DataFrame(resultats)

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


def AgeBassins(filtered_data, group_column):
    """
    Calcule la répartition par âge des bassins.
    - Avec group_column : 1 ligne par commune, colonnes = tranches d'âge (+ Pas de données), 0 si absence.
    - Sans group_column : répartition globale par tranche d'âge.
    """
    df_ages = filtered_data[Data.QUERY_BASSINS].copy()
    df_ages[Data.ANNEE_CONSTRUCTION] = df_ages[Data.ANNEE_CONSTRUCTION].fillna(
        -1)
    year = datetime.now().year

    # Calcul âge uniquement pour les années valides
    df_ages_calcul = df_ages[df_ages[Data.ANNEE_CONSTRUCTION] != -1].copy()
    df_ages_calcul['age'] = year - \
        df_ages_calcul[Data.ANNEE_CONSTRUCTION].astype(int)

    # Tranches d'âge
    bornes = [0, 10, 20, 30, float('inf')]
    labels = [Data.AGE_0_10, Data.AGE_11_20, Data.AGE_21_30, Data.AGE_OVER_30]

    df_ages_calcul['tranche_age'] = pd.cut(
        df_ages_calcul['age'], bins=bornes, labels=labels, right=False
    )

    # Réinjecter les tranches calculées et compléter "Pas de données"
    df_ages.loc[df_ages_calcul.index,
                'tranche_age'] = df_ages_calcul['tranche_age']
    df_ages['tranche_age'] = df_ages['tranche_age'].astype('category')
    if Data.PAS_DE_DONNEES not in df_ages['tranche_age'].cat.categories:
        df_ages['tranche_age'] = df_ages['tranche_age'].cat.add_categories([
                                                                           Data.PAS_DE_DONNEES])
    df_ages['tranche_age'] = df_ages['tranche_age'].fillna(Data.PAS_DE_DONNEES)

    # Ordre final des colonnes de sortie
    out_cols = labels + [Data.PAS_DE_DONNEES]

    if group_column:
        # Comptage par (commune, tranche)
        groupes = df_ages.groupby([group_column, 'tranche_age'])
        indicateur = groupes[Data.ID_BASSIN].nunique(
        ).reset_index(name='nb_bassins')

        # Pivot -> 1 ligne par commune, colonnes = tranches
        wide = indicateur.pivot(
            index=group_column, columns='tranche_age', values='nb_bassins').fillna(0)

        # S'assurer que toutes les colonnes de tranches existent
        for col in out_cols:
            if col not in wide.columns:
                wide[col] = 0

        # Base des communes complètes (67)
        base = filtered_data[Data.QUERY_CANAP][group_column].drop_duplicates(
        ).to_frame()

        # Left join pour inclure toutes les communes
        dff = base.merge(wide.reset_index(), on=group_column,
                         how='left').fillna(0)

        # Ordonner colonnes et caster en int
        dff = dff[[group_column] + out_cols]
        for col in out_cols:
            dff[col] = dff[col].astype(int)

    else:
        # Vue globale : une ligne par tranche
        groupes = df_ages.groupby('tranche_age', observed=False)
        indicateur = groupes[Data.ID_BASSIN].nunique(
        ).reset_index(name='nb_bassins')
        dff = indicateur.copy()

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


def ES_NV(filtered_data, group_column):
    """
    Calcule l'état de santé des réseaux non visitables.
    - Avec group_column : 1 ligne par commune, colonnes = états (km), zéros si absence.
    - Sans group_column : tableau global Etat / km / %.
    """
    df_Sante_NV = filtered_data[Data.QUERY_CANAEXP][
        filtered_data[Data.QUERY_CANAEXP][Data.HAUTEUR] < 150
    ].copy()

    # Mapping des notes -> libellés
    note_mapping = {
        Data.G1: Data.ETAT_BON,
        Data.G2: Data.ETAT_CORRECT,
        Data.G3: Data.ETAT_DEGRADE,
        Data.G4: Data.ETAT_MAUVAIS,
        Data.G0: Data.ITV_INCOMPLETES,
    }
    df_Sante_NV[Data.NOTE_INDIG] = (
        df_Sante_NV[Data.NOTE_INDIG].map(
            note_mapping).fillna(Data.PAS_DE_DONNEES)
    )

    etats = [
        Data.ETAT_BON,
        Data.ETAT_CORRECT,
        Data.ETAT_DEGRADE,
        Data.ETAT_MAUVAIS,
        Data.ITV_INCOMPLETES,
        Data.PAS_DE_DONNEES,
    ]

    if group_column:
        # Somme des longueurs (km) par (commune, état)
        groupes = df_Sante_NV.groupby([group_column, Data.NOTE_INDIG])
        res = (
            groupes.apply(
                lambda x: x.drop_duplicates(subset=Data.ID_CANA_EXP)[
                    Data.LONGUEUR].sum() / 1000
            )
            .round()
            .reset_index(name=Indicators.LONGUEUR_SUM)
        )

        # Pivot -> 1 ligne par commune, colonnes = états
        dff_wide = (
            res.pivot(index=group_column, columns=Data.NOTE_INDIG,
                      values=Indicators.LONGUEUR_SUM)
            .fillna(0)
        )

        # S'assurer que toutes les colonnes d'état existent
        for e in etats:
            if e not in dff_wide.columns:
                dff_wide[e] = 0

        # Inclure TOUTES les communes depuis le référentiel
        base = (
            filtered_data[Data.QUERY_CANAP][group_column]
            .drop_duplicates()
            .to_frame()
        )
        dff = (
            base.merge(dff_wide.reset_index(), on=group_column, how="left")
                .fillna(0)
        )

        # Ordonner les colonnes : commune + états
        dff = dff[[group_column] + etats]

        # Types propres (entiers en km comme ton arrondi)
        for e in etats:
            dff[e] = dff[e].astype(int)

    else:
        # Vue globale : Etat / km / %
        groupes = df_Sante_NV.groupby(Data.NOTE_INDIG)
        res = (
            groupes.apply(
                lambda x: x.drop_duplicates(subset=Data.ID_CANA_EXP)[
                    Data.LONGUEUR].sum() / 1000
            )
            .round()
            .reset_index(name=Indicators.LONGUEUR_SUM)
        )
        dff = pd.DataFrame(res)

        total_longueur = dff[Indicators.LONGUEUR_SUM].sum()
        if dff.empty or total_longueur == 0:
            dff[Indicators.POURCENTAGE] = 0
        else:
            dff[Indicators.POURCENTAGE] = (
                (dff[Indicators.LONGUEUR_SUM] * 100) / total_longueur
            ).round()

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


def ES_V(df_vis, group_column):
    """
    Calcule l'état de santé des réseaux visitables.
    - Avec group_column : 1 ligne par commune, colonnes = états (en km), zéros si absence.
    - Sans group_column : tableau global Etat / km / %.
    """
    if group_column:
        # Somme des longueurs (km) par (commune, état)
        groupes = df_vis.groupby([group_column, Data.ET_7])
        res = (
            groupes.apply(
                lambda x: x.drop_duplicates(subset=Data.ID_CANAP)[
                    Data.LONGUEUR].sum() / 1000,
                include_groups=False
            )
            .round()
            .reset_index(name=Indicators.LONGUEUR_SUM)
        )

        # Pivot -> 1 ligne par commune, colonnes = états
        dff_wide = (
            res.pivot(index=group_column, columns=Data.ET_7,
                      values=Indicators.LONGUEUR_SUM)
            .fillna(0)
        )

        # Inclure toutes les communes du df_vis (même si aucune longueur pour un état)
        base = df_vis[[group_column]].drop_duplicates()
        dff = base.merge(dff_wide.reset_index(),
                         on=group_column, how="left").fillna(0)

        # Types propres (km arrondis comme dans ton code)
        for col in dff.columns:
            if col != group_column:
                dff[col] = dff[col].astype(int)

    else:
        groupes = df_vis.groupby(Data.ET_7)
        resultats = (
            groupes.apply(
                lambda x: x.drop_duplicates(subset=Data.ID_CANAP)[
                    Data.LONGUEUR].sum() / 1000,
                include_groups=False
            )
            .round()
            .reset_index(name=Indicators.LONGUEUR_SUM)
        )
        dff = pd.DataFrame(resultats)

        # % global (toutes communes confondues)
        total_longueur = dff[Indicators.LONGUEUR_SUM].sum()
        if dff.empty or total_longueur == 0:
            dff[Indicators.POURCENTAGE] = 0
        else:
            dff[Indicators.POURCENTAGE] = (
                (dff[Indicators.LONGUEUR_SUM] * 100) / total_longueur
            ).round()

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


def ES_STR_EP(filtered_data, df_tremies_inspections, group_column):
    """
    Calcule l'état de santé des trémies (STR EP).
    """
    current_year = datetime.now().year

    df_tremies_inspections[Data.NUMERO] = df_tremies_inspections[Data.NUMERO].astype(
        int)
    df_merged = pd.merge(
        filtered_data[Data.QUERY_TREMIE], df_tremies_inspections, on=Data.NUMERO, how='left')

    # Mapping de l'état
    etat_col = Data.CAMPAGNE_FORMAT.format(current_year-1)
    note_mapping = {
        1: Data.ETAT_BON, 2: Data.ETAT_CORRECT,
        3: Data.ETAT_DEGRADE, 4: Data.ETAT_MAUVAIS
    }
    if etat_col in df_merged.columns:
        df_merged['Etat'] = df_merged[etat_col].map(note_mapping)
    df_merged['Etat'] = df_merged['Etat'].fillna(Data.PAS_DE_DONNEES)

    if group_column:
        groupes = df_merged.groupby([group_column, 'Etat'])
        resultat = groupes[Data.ID_TREMIE].nunique().reset_index(name='nbr')
        dff = pd.DataFrame(resultat)

    else:
        groupes = df_merged.groupby('Etat')
        resultats = groupes[Data.ID_TREMIE].nunique().reset_index(name='nbr')
        dff = pd.DataFrame(resultats)

    total_ouvrages = sum(dff['nbr'])
    if dff.empty or total_ouvrages == 0:
        dff[Indicators.POURCENTAGE] = 0
    else:
        dff[Indicators.POURCENTAGE] = round(
            (dff['nbr'] * 100) / total_ouvrages)

    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff

# Nombre de branchements connu et estimé


def NBCE(filtered_data, group_column, Ratio):
    if group_column:
        groupes = filtered_data[Data.QUERY_CANAS].groupby(group_column)
        grp_canap = filtered_data[Data.QUERY_CANAP].groupby(group_column)

        resultats = groupes[Data.ID_CANAS].nunique().reset_index()
        resultat_tot = grp_canap.apply(lambda x: x.drop_duplicates(subset=Data.ID_CANAP)[
                                       Data.LONGUEUR].sum()).reset_index(name='somme_longueur')

        resultat_tot.columns = [group_column, 'longueur_res']
        resultats.columns = [group_column, 'branch_connus']
        # Fusionner les résultats
        dff = pd.merge(resultat_tot, resultats, on=group_column, how='outer')
        dff['branch_estimes'] = round(dff['longueur_res'] * Ratio, -3)
        dff['branch_tot'] = dff['branch_estimes'] + dff['branch_connus']

        dff = dff.fillna(0)

    else:
        brch_connu = filtered_data[Data.QUERY_CANAS][Data.ID_CANAS].nunique()
        lin_tot = filtered_data[Data.QUERY_CANAP].drop_duplicates(subset=Data.ID_CANAP)[
            Data.LONGUEUR].sum()
        brch_estime = round(lin_tot * Ratio, -3)
        brch_tot = brch_estime + brch_connu
        dff = pd.DataFrame({'longueur_res': [lin_tot], 'branch_connus': [
                           brch_connu], 'branch_estimes': [brch_estime], 'branch_tot': [brch_tot]})
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)
        return (dff)
    else:
        dff_bis = pd.DataFrame({Indicators.CONNAISSANCE: [Indicators.CONNUES, Indicators.ESTIMES], 'nb_brch': [
                               dff['branch_connus'][0], dff['branch_estimes'][0]]})
        dff_bis[Indicators.POURCENTAGE] = round(
            (dff_bis['nb_brch'] * 100) / (sum(dff_bis['nb_brch'])))
        return (dff)


def ES_STEU(filtered_data, df_steu, group_column):
    """
    Calcule l'état de santé des stations STEU (EU_U).
    - Avec group_column : 1 ligne par commune, colonnes = états, zéros si absence.
    - Sans group_column : Etat / nbr / Pourcentage (global).
    """
    current_year = datetime.now().year
    campagne_col = f'Campagne {current_year - 1}'

    # Mapping manuel des identifiants STEU (si besoin pour libellés)
    steu = {
        13: 'Genay', 6: 'Fontaines', 8: 'Jonage', 1: 'La Feyssine',
        11: 'Lissieu Le Bourg', 12: 'Lissieu Sémanet', 10: 'Meyzieu',
        5: 'Neuville', 7: 'Pierre-Bénite', 17: 'Quincieux',
        2: 'Saint-Fons', 4: 'Saint-Germain', 3: 'Givors'
    }

    # --- Données référentiel STEU ---
    df_infos = filtered_data[Data.QUERY_STEU].copy()
    df_infos['N°'] = df_infos[Data.NOM_STEU].apply(
        lambda x: x.split()[1].split('_')[0] if isinstance(
            x, str) and len(x.split()) > 1 else None
    )
    df_infos = df_infos[df_infos['N°'].notna(
    ) & df_infos['N°'].apply(str.isnumeric)]
    df_infos['N°'] = df_infos['N°'].astype(str)
    df_infos[Data.NOM_STEU] = df_infos[Data.ID_STEU].map(
        steu).fillna(df_infos[Data.NOM_STEU])

    # --- Données d'état (df_steu) ---
    df_etat = df_steu.copy()
    df_etat['N°'] = df_etat['N°'].astype(str)

    # --- Jointure ---
    df_merged = pd.merge(df_etat, df_infos, on='N°', how='inner')

    # --- Mapping des états (num -> libellé) ---
    note_mapping = {
        1: 'État bon',
        2: 'État correct',
        3: 'État dégradé',
        4: 'État mauvais'
    }
    if campagne_col in df_merged.columns:
        df_merged['Etat'] = df_merged[campagne_col].map(
            note_mapping).fillna('Pas de données')
    else:
        df_merged['Etat'] = 'Pas de données'

    etats = ['État bon', 'État correct', 'État dégradé',
             'État mauvais', 'Pas de données']

    # --- Agrégation ---
    if group_column:
        # Comptage par (commune, état)
        grouped = (
            df_merged.groupby([group_column, 'Etat'])['N°']
                     .nunique()
                     .reset_index(name='nbr')
        )

        # Pivot -> 1 ligne par commune, colonnes = états
        wide = grouped.pivot(index=group_column,
                             columns='Etat', values='nbr').fillna(0)

        # S'assurer que toutes les colonnes d'états existent
        for e in etats:
            if e not in wide.columns:
                wide[e] = 0

        # Inclure toutes les communes même sans STEU/etat
        base = filtered_data[Data.QUERY_CANAP][group_column].drop_duplicates(
        ).to_frame()
        dff = base.merge(wide.reset_index(), on=group_column,
                         how='left').fillna(0)

        # Ordonner les colonnes : commune + états
        dff = dff[[group_column] + etats]

        # Types propres
        for e in etats:
            dff[e] = dff[e].astype(int)

    else:
        dff = (
            df_merged.groupby('Etat')['N°']
            .nunique()
            .reset_index(name='nbr')
        )
        total = dff['nbr'].sum()
        dff['Pourcentage'] = round(
            (dff['nbr'] * 100) / total, 2) if total > 0 else 0

    # Cas vide
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


def ES_STR(filtered_data, df_str, group_column):
    """
    Calcule l'état de santé des ouvrages STR (EU_U).
    - Avec group_column : 1 ligne par commune, colonnes = états (nb d'ouvrages), 0 si absence.
    - Sans group_column : tableau global Etat / nbr / Pourcentage.
    """
    current_year = datetime.now().year
    campagne_col = f'Campagne {current_year - 1}'

    # --- Récupération et nettoyage des données STR ---
    df_infos = filtered_data[Data.QUERY_STARE].copy()
    df_infos = df_infos[df_infos[Data.NUMERO].notna() & (
        df_infos[Data.NUMERO] != 0)]
    df_infos['N°'] = df_infos[Data.NUMERO].astype(str)

    # --- Préparation de df_str (notes d'état) ---
    df_etat = df_str.copy()
    df_etat['N°'] = df_etat['N°'].astype(str)

    # --- Jointure ---
    df_merged = pd.merge(df_infos, df_etat, on='N°', how='left')

    # --- Mapping des états ---
    note_mapping = {1: 'État bon', 2: 'État correct',
                    3: 'État dégradé', 4: 'État mauvais'}
    if campagne_col in df_merged.columns:
        df_merged['Etat'] = df_merged[campagne_col].map(
            note_mapping).fillna('Pas de données')
    else:
        df_merged['Etat'] = 'Pas de données'

    # --- Déduplication (1 ligne par STR) ---
    df_merged = df_merged.drop_duplicates(subset='N°')

    etats = ['État bon', 'État correct', 'État dégradé',
             'État mauvais', 'Pas de données']

    # --- Agrégation ---
    if group_column:
        # Comptage par (commune, état)
        grouped = (df_merged.groupby([group_column, 'Etat'])['N°']
                   .nunique()
                   .reset_index(name='nbr'))

        # Pivot -> 1 ligne par commune, colonnes = états
        wide = grouped.pivot(index=group_column,
                             columns='Etat', values='nbr').fillna(0)

        # S'assurer que toutes les colonnes d'états existent
        for e in etats:
            if e not in wide.columns:
                wide[e] = 0

        # Inclure toutes les communes
        base = filtered_data[Data.QUERY_CANAP][group_column].drop_duplicates(
        ).to_frame()
        dff = base.merge(wide.reset_index(), on=group_column,
                         how='left').fillna(0)

        # Ordonner colonnes et caster en int
        dff = dff[[group_column] + etats]
        for e in etats:
            dff[e] = dff[e].astype(int)

    else:
        dff = (df_merged.groupby('Etat')['N°']
               .nunique()
               .reset_index(name='nbr'))
        total = dff['nbr'].sum()
        dff['Pourcentage'] = round(
            (dff['nbr'] * 100) / total, 2) if total > 0 else 0

    # Cas vide
    if dff.empty:
        dff.loc[0] = [0] * len(dff.columns)

    return dff


def NBEOT(results, group_column):
    if group_column:
        # NBEOT par groupe : somme des valeurs NBEO pour chaque groupe
        if isinstance(results, pd.DataFrame) and not results.empty:
            # Créer un DataFrame avec la somme par groupe
            results = results.groupby(group_column).sum().reset_index()
        else:
            # Si NBEO est vide, créer un DataFrame vide avec la bonne structure
            results = pd.DataFrame(columns=[group_column, 'Total'])
    else:
        # Sans regroupement : somme totale comme avant
        if isinstance(results, pd.DataFrame):
            results = pd.DataFrame(
                {'nb_total': [results.sum(numeric_only=True).sum()]})
        else:
            results = 0
    return results
