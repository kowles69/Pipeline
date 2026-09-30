from indicators import functions as indicator_functions
from utils.constants import Data, Indicators


def function(results, processed_data, group_column):
    # CONNAITRE LES PATRIMOINES
    # COLLECTEURS
    # Calcule le réseaux unitaires.
    results['LRU'] = indicator_functions.LRU(processed_data, group_column)
    # Calcule le réseaux eaux usées.
    results['LREU'] = indicator_functions.LREU(processed_data, group_column)
    # Calcule le réseaux total (Unitaire + Usée).
    results['LEP'] = indicator_functions.LEP(
        processed_data[Data.QUERY_CANAP], group_column)
    # Calcule le linéaire de réseaux visitables et non-visitables.
    results['LRV'] = indicator_functions.LRV(
        processed_data[Data.QUERY_CANAP], group_column)
    # Calcule le linéaire de réseaux par classe de précision (A, B, C).
    results['LinClass'] = indicator_functions.LinClass(
        processed_data, group_column)
    # Calcule le linéaire de réseaux par connaissance des matériaux (Connus, Estimés).
    results['ConMat'] = indicator_functions.ConMat(
        processed_data, group_column)
    # Calcule le linéaire de réseaux par connaissance de l'année de pose (Connue, Estimée).
    results['ConAge'] = indicator_functions.ConAge(
        processed_data, group_column)
    # Calcule le linéaire de réseaux par famille de matériau présumé.
    results['LRM'] = indicator_functions.LRM(processed_data, group_column)
    # Calcule la répartition des réseaux par tranche d'âge.
    results['AR'] = indicator_functions.AR(processed_data, group_column)
    # Calcule l'âge moyen des réseaux (années de pose connues uniquement).
    results['AMR'] = indicator_functions.AMR(processed_data, group_column)
    # Calcule l'âge moyen des réseaux (connu + estimé)
    results['AMR_ESTIME'] = indicator_functions.AMR_ESTIME(processed_data, group_column)
    # Calcule le nombre de parcelles privées traversées par les réseaux.
    results['NPPTR'] = indicator_functions.NPPTR(
        processed_data, processed_data[Data.GDF_CAD_OVERLAPS], group_column)
    # Calcule le linéaire de réseaux situé sur des parcelles ou voies privées.
    results['LRSPVP'] = indicator_functions.LRSPVP(
        processed_data, processed_data[Data.CANEXP_CADASTRE_MERGED], processed_data[Data.CANEXP_VOIE_MERGED], group_column)
    # Total à régulariser TO DO
    # Régularisés TO DO
    # Calcule la valeur patrimoniale à neuf des réseaux.
    results['VPR'] = indicator_functions.VPR(processed_data, group_column, processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT][Indicators.TYPE_OUVRAGE] == Indicators.OUVRAGE_RESEAU_VISITABLE]
                                             [Indicators.RATIO_CHOISI].iloc[0], processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT][Indicators.TYPE_OUVRAGE] == Indicators.OUVRAGE_RESEAU_NON_VISITABLE][Indicators.RATIO_CHOISI].iloc[0])

# BRANCHEMENTS
    # Calcule le nombre de branchements connus et estimés. Un ratio de branchements par mètre linéaire est utilisé pour l'estimation.
    # Note: La fonction NBCE de l'ancien fichier nécessitait un ratio non disponible ici. NBr est utilisé comme substitut pour le nombre connu.
    results['NBCE'] = indicator_functions.NBCE(
        processed_data, group_column, Ratio=(300000 - 54246) / 3298416)
    # Calcule la valeur patrimoniale à neuf des branchements.
    results['VPBr'] = indicator_functions.VPBr(processed_data, group_column, processed_data[Data.DF_RATIO_COUT]
                                               [processed_data[Data.DF_RATIO_COUT][Indicators.TYPE_OUVRAGE] == Indicators.OUVRAGE_BRANCHEMENT][Indicators.RATIO_CHOISI].iloc[0])
# OUVRAGES
    # Dénombre les stations de traitements des eaux usées.
    results['NSTEU'] = indicator_functions.NSTEU(processed_data, group_column)
    # Dénombre les stations de refoulement.
    results['NSTR'] = indicator_functions.NSTR(processed_data, group_column)
    # Dénombre les filtres plantés de roseaux.
    results['NFPR'] = indicator_functions.NFPR(processed_data, group_column)
    # Dénombre les déversoirs d'orage.
    results['NDO'] = indicator_functions.NDO(processed_data, group_column)
    # Dénombre les dessableurs.
    results['NDes'] = indicator_functions.NDes(processed_data, group_column)
    # Valeur patrimoniale à neuf des stations de traitements des eaux usées.
    results['VPSTEU'] = indicator_functions.VPSTEU(processed_data, processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT]
                                                   [Indicators.TYPE_OUVRAGE] == 'STEU '][Indicators.RATIO_CHOISI].iloc[0], group_column)
    # Valeur patrimoniale à neuf des stations de refoulement
    results['VPSTR'] = indicator_functions.VPSTR(processed_data, processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT]
                                                 [Indicators.TYPE_OUVRAGE] == 'STR/trémie '][Indicators.RATIO_CHOISI].iloc[0], group_column)
    # Valeur patrimoniale à neuf des filtres plantés de roseaux
    results['VPFPR'] = indicator_functions.VPFPR(processed_data, processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT]
                                                 [Indicators.TYPE_OUVRAGE] == 'FPR '][Indicators.RATIO_CHOISI].iloc[0], group_column)
    # Valeur à neuf des déversoirs d'orage : TO DO
    # Valeur à neuf des dessableurs : TO DO
    # Dénombre les Stations de traitements des eaux usées récolées : TO DO
    # Dénombre les Stations de refoulement récolées
    results['NSR'] = indicator_functions.NSR(
        processed_data[Data.DF_RECOLEMENT_STR], group_column)
    # Dénombre les filtres plantés de roseaux récolées
    # results['NFR'] = indicator_functions.NFR(processed_data['df_dossier_fpr'], group_column)
    # Dénombre les déversoirs d'orage recolés : TO DO
    # Dénombre les dessableurs recolés : TO DO
    # Foncier à acquérir des STEU : TO DO
    # Foncier à acquérir des STR : TO DO
    # Foncier à acquérir des FPR : TO DO
    # Foncier à acquérir des DO : TO DO
    # Foncier à acquérir des dessableurs : TO DO
    # Calcule tranche d'âge des stations des traitement des eaux usées : TO DO
    results['AgeSTEU'] = indicator_functions.AgeSTEU(
        processed_data, group_column)
    # Calcule tranche d'âge des stations de refoulement
    results['AgeSTR'] = indicator_functions.AgeSTR(
        processed_data, group_column)
# RESEAU ELECTRIQUE
    # Calcule le linéaire de réseaux secs (courant faible et fort).
    results['LRSFa'] = indicator_functions.LRSFa(
        processed_data[Data.GDF_GLOB_EU_U], group_column)
    # Calcule la Précision planimétrique
    results['LIN_SEC_CLASS'] = indicator_functions.LinSecClass(
        processed_data[Data.GDF_GLOB_EP], processed_data, group_column)
# CONNAITRE L'ETAT DE SANTE
# COLLECTEURS : linéaire inspecté
    # Calcule le linéaire de réseaux inspecté par ITV (Inspection Télévisuelle).
    results['LITV'] = indicator_functions.LITV(
        processed_data, processed_data[Data.VALEURS_UNIQUES_ITV], processed_data[Data.VALEURS_UNIQUES_ANNUELLES_ITV], group_column)
    # Calcule le linéaire inspecté en DIAG.
    results['LDIAG_PREDIAG_DIAG'] = indicator_functions.LDiagPrediag(
        processed_data[Data.DF_VIS], group_column, None, Data.DIAG)
    # Calcule le linéaire inspecté en PREDIAG.
    results['LDIAG_PREDIAG_PREDIAG'] = indicator_functions.LDiagPrediag(
        processed_data[Data.DF_VIS], group_column, None, Data.PREDIAG)
# COLLECTEURS : état de santé
    # Calcule l'état de santé des réseaux non visitables.
    results['ES_NV'] = indicator_functions.ES_NV(processed_data, group_column)
    # Calcule l'état de santé des réseaux visitables.
    results['ES_V'] = indicator_functions.ES_V(
        processed_data[Data.DF_VIS], group_column)
# BRANCHEMENTS : état de santé
    # Logique pour l'état de santé des branchements non fournie dans les fichiers.
    results['ES_BR'] = 'TO DO'
# OUVRAGES : nombre d'inspections
    # Nombre total d'inspections des STEU
    results['NISTEU'] = indicator_functions.NISTEU(
        processed_data, processed_data[Data.INS_STEU], group_column)
    # Nombre total d'inspections des STR
    results['NISTR'] = indicator_functions.NISTR(
        processed_data, processed_data[Data.INS_STEU], group_column)
    # Nombre total d'inspections des FPR : TO DO
    # Nombre d'inspection des FPR dans l'année : TO DO
    # Pourcentage par rapport au total des ouvrages des FPR : TO DO
# OUVRAGES : état de santé
    # Etat de santé des STEU
    results['ES_STEU'] = indicator_functions.ES_STEU(
        processed_data, processed_data[Data.DF_STEU_ETAT], group_column)
    # Etat de santé des STR
    results['ES_STR'] = indicator_functions.ES_STR(
        processed_data, processed_data['df_str_etat'], group_column)
    # Etat de santé dees FPR : TO DO
# PROGRAMME DE TRAVAUX
# COLLECTEURS
    # Calcule le linéaire total d'idées de travaux sur les réseaux.
    results['LRIT'] = indicator_functions.LRIT(
        processed_data[Data.DF_IDEES_TRAVAUX], group_column)
    # Total réhabilité : TO DO
    # Extension annuelle : TO DO
    # Taux annuel de renouvellement : TO DO

# BRANCHEMENTS
    # Branchements réhabilités : TO DO
# OUVRAGES
    # STEU réhabilitées : TO DO
    # STR réhabilites : TO DO
    # FPR réhabilités : TO DO

    return results
