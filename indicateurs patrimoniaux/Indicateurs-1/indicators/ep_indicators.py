from indicators import functions as indicator_functions
from utils.constants import Data, Indicators


def function(results, processed_data, group_column):
    # CONNAITRE LES PATRIMOINES
    # COLLECTEURS
    # Calcule le linéaire de réseaux visitables et non-visitables.
    results['LRV'] = indicator_functions.LRV(
        processed_data[Data.QUERY_CANAP], group_column)
    # Calcule le linéaire total de réseaux d'eaux pluviales.
    results['LEP'] = indicator_functions.LEP(
        processed_data[Data.QUERY_CANAP], group_column)
    # Calcule le linéaire de réseaux par classe de précision (A, B, C).
    results['LIN_CLASS'] = indicator_functions.LinClass(
        processed_data, group_column)
    # Calcule le linéaire de réseaux par connaissance des matériaux (Connus, Estimés).
    results['CON_MAT'] = indicator_functions.ConMat(
        processed_data, group_column)
    # Calcule le linéaire de réseaux par connaissance de l'année de pose (Connue, Estimée).
    results['CON_AGE'] = indicator_functions.ConAge(
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
    # TODO Total à régulariser - Fonction à dev
    # TODO Régularisés  - Fonction à dev
    # Calcule la valeur patrimoniale à neuf des réseaux.
    results['VPR'] = indicator_functions.VPR(processed_data, group_column, processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT][Indicators.TYPE_OUVRAGE] == Indicators.OUVRAGE_RESEAU_VISITABLE]
                                             [Indicators.RATIO_CHOISI].iloc[0], processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT][Indicators.TYPE_OUVRAGE] == Indicators.OUVRAGE_RESEAU_NON_VISITABLE][Indicators.RATIO_CHOISI].iloc[0])
    # BRANCHEMENTS
    # Calcule le nombre de branchements connus et estimés. Un ratio de branchements par mètre linéaire est utilisé pour l'estimation.
    results['NBCE'] = indicator_functions.NBCE(
        processed_data, group_column, Ratio=(300000 - 54246) / 3298416)
    # Calcule la valeur patrimoniale à neuf des branchements.
    results['VP_BR'] = indicator_functions.VPBr(processed_data, group_column, processed_data[Data.DF_RATIO_COUT]
                                                [processed_data[Data.DF_RATIO_COUT][Indicators.TYPE_OUVRAGE] == Indicators.OUVRAGE_BRANCHEMENT][Indicators.RATIO_CHOISI].iloc[0])
    # OUVRAGES
    # Dénombre les bassins enterrés et à ciel ouvert.
    results['NBEO'] = indicator_functions.NBEO(
        processed_data[Data.QUERY_BASSINS], group_column)
    # Dénombre total bassins
    results['NBEOT'] = indicator_functions.NBEOT(results['NBEO'], group_column)
    # Dénombre les linéaires d'infiltration.
    results['NLI'] = indicator_functions.NLi(
        processed_data[Data.QUERY_OGEP], group_column)
    # Dénombre les noues (simples et composées).
    results['NNO'] = indicator_functions.NNo(
        processed_data[Data.QUERY_OGEP], group_column)
    # Dénombre les tranchées (y compris tranchées de Stockholm).
    results['NTR_EP'] = indicator_functions.NTr(
        processed_data[Data.QUERY_OGEP], group_column)
    # Dénombre les arbres de pluie.
    results['NAP'] = indicator_functions.NAP(processed_data, group_column)
    # Dénombre les puits d'infiltration.
    results['NPI'] = indicator_functions.NPI(processed_data, group_column)
    # Dénombre les dessableurs.
    results['NDES'] = indicator_functions.NDes(processed_data, group_column)
    # Dénombre les trémies.
    results['NT'] = indicator_functions.NT(processed_data, group_column)
    # TODO Bassin versant connu - Fonction à dev
    # Calcule la valeur patrimoniale à neuf des bassins.
    results['VP_BASSINS'] = indicator_functions.VPBassins(processed_data, processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT][Indicators.TYPE_OUVRAGE] == Indicators.OUVRAGE_BASSINS_CIEL_OUVERT]
                                                          [Indicators.RATIO_CHOISI].iloc[0], processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT][Indicators.TYPE_OUVRAGE] == Indicators.OUVRAGE_BASSINS_ENTERRES][Indicators.RATIO_CHOISI].iloc[0], group_column)
    # Calcule la valeur patrimoniale à neuf des ouvrages de gestion des eaux pluviales (OGEP).
    results['VP_OGEP'] = indicator_functions.VPOGEP(processed_data, processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT]
                                                    [Indicators.TYPE_OUVRAGE] == Indicators.OUVRAGE_LIN_INFILTRATION][Indicators.RATIO_CHOISI].iloc[0], group_column)
    # TODO VP noue - Fonction à dev
    # TODO VP tranchée - Fonction à dev
    # Calcule la valeur patrimoniale à neuf des arbres de pluie.
    results['VP_AP'] = indicator_functions.VPAP(processed_data, processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT]
                                                [Indicators.TYPE_OUVRAGE] == Indicators.OUVRAGE_ARBRES_PLUIE][Indicators.RATIO_CHOISI].iloc[0], group_column)
    # Calcule la valeur patrimoniale à neuf des puits d'infiltration.
    results['VP_PI'] = indicator_functions.VPPI(processed_data, processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT]
                                                [Indicators.TYPE_OUVRAGE] == Indicators.OUVRAGE_PUITS_INFILTRATION][Indicators.RATIO_CHOISI].iloc[0], group_column)
    # TODO VP - Fonction à dev
    # Calcule la valeur patrimoniale à neuf des trémies.
    results['VP_TREM'] = indicator_functions.VPTREM(processed_data, processed_data[Data.DF_RATIO_COUT][processed_data[Data.DF_RATIO_COUT]
                                                    [Indicators.TYPE_OUVRAGE] == Indicators.OUVRAGE_STR_TREMIE][Indicators.RATIO_CHOISI].iloc[0], group_column)
    # TODO VP result bassin versant connu - Fonction à dev
    # Dénombre les bassins récolés.
    results['NBR'] = indicator_functions.NBR(
        processed_data['df_recolement_bassins'], group_column)
    # TODO nb bassins rec Détail - Fonction à dev
    # TODO Recol ogep + ogep détail - Fonction à dev
    # Dénombre les arbres de pluie récolés.
    results['NAPR'] = indicator_functions.NAPR(
        processed_data[Data.DF_RECOLEMENT_AP][processed_data[Data.DF_RECOLEMENT_AP][Data.OUVRAGE] == Data.ARBRE_DE_PLUIE], group_column)
    # TODO recol ppi - Fonction à dev
    # Dénombre les dessableurs récolés.
    results['NDESR'] = indicator_functions.NDesR(processed_data, group_column)
    # Dénombre les trémies récolées.
    results['NTR_RECOLES'] = indicator_functions.NTR(
        processed_data[Data.DF_RECOLEMENT_TREMIES], group_column)
    # TODO recol result bassin versant connu - Fonction à dev
    # TODO foncier à acquérir - Fonction à dev
    # Calcule la répartition par âge des bassins.
    results['AGE_BASSINS'] = indicator_functions.AgeBassins(
        processed_data, group_column)
    # Calcule la répartition par âge des trémies (STR EP).
    # APSTR est utilisé car AgeSTR_EP n'existe pas dans les fichiers fournis
    results['AGE_STR_EP'] = indicator_functions.AgeSTR_EP(
        processed_data, group_column)
    # RESEAU ELECTRIQUE
    # Calcule le linéaire de réseaux secs (courant faible et fort).
    results['LRSFA'] = indicator_functions.LRSFa(
        processed_data[Data.GDF_GLOB_EP], group_column)
    # Calcule le linéaire de réseaux secs (courant faible et fort) par classe de précision.
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
    results['ES_BR'] = 'TODO'
    # OUVRAGES : nombre d'inspections
    # NBEO NLI NAP etc pour la première colonne
    # Bassins inspectés TODO
    # Calcule le nombre d'inspection sur les linéaires d'infiltration dans l'année
    results['LLI'] = indicator_functions.LLI(processed_data, group_column)
    # Arbre de pluie inspecté TODO
    # Puit d'infiltration inspecté TODO
    # Calcule le nombre d'inspections sur les STR.
    results['NI_STR'] = indicator_functions.NISTR(
        processed_data, processed_data[Data.INS_STR], group_column)
    # OUVRAGES : état de santé
    # Logique pour l'état de santé des bassins non fournie dans les fichiers.
    # TODO results['ES_BASSINS'] = 'TO DO'
    # Calcule l'état de santé des trémies (STR EP).
    results['ES_STR_EP'] = indicator_functions.ES_STR_EP(
        processed_data, processed_data[Data.DF_TREMIES_ETAT], group_column)
    # Logique pour l'état de santé des linéaires d'infiltration non fournie.
    # TODO results['ES_LI'] = 'TO DO'
    # Logique pour l'état de santé des puits d'infiltration non fournie.
    # TODO results['ES_PI'] = 'TO DO'
# PROGRAMME DE TRAVAUX
    # COLLECTEURS
    # Calcule le linéaire total d'idées de travaux sur les réseaux.
    results['LRIT'] = indicator_functions.LRIT(
        processed_data[Data.DF_IDEES_TRAVAUX], group_column)
    # TODO total rehab
    # TODO extension anuelle
    # TODO taux annuel renouvellement
    # BRANCHEMENTS
    # TODO branchement réhabilités
    # OUVRAGES
    # TODO Ouvrages EP créés
    # TODO Bassins réhabilités
    # TODO linéaires d'infiltration réhabilités
    # TODO STR réhabilitées
    return results
