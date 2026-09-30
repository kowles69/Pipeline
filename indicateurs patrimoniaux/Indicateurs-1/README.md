# Nom du Projet

Description du projet...

## Installation

1.  **Cloner le projet**
    ```bash
    git clone [URL_DU_PROJET]
    cd [NOM_DU_DOSSIER]
    ```

2.  **Créer et activer un environnement virtuel**
    ```bash
    # Créer l'environnement
    python -m venv .venv

    # Activer l'environnement
    # Sur Windows (PowerShell)
    .venv\Scripts\Activate.ps1
    # Sur Linux/macOS
    source .venv/bin/activate
    ```

3.  **Installer les dépendances**
    ```bash
    python -m pip install --upgrade pip
    pip install -e .
    ```

4.  **Configurer l'interpréteur dans VS Code**
    Ouvrez la palette de commandes (`Ctrl+Shift+P`) et tapez `Python: Select Interpreter`. Choisissez l'interpréteur de votre environnement `.venv`.

5. **Fonctions disponibles**
    LRU  		: Linéaire de réseaux Unitaire  
    LREU 		: Linéaire de réseaux Eaux Usées  
    LEP  		: Linéaire de réseaux  
    LRM  		: Linéaire de réseaux par famille de materiau (au global)  
    LRMC 		: Linéaire de réseaux avec matériaux connu  
    LRME 		: Linéaire de réseaux avec matériaux estimé  
    LRM_E_C 	: Linéaire de réseaux avec matériaux connus et estimes  
    LRV 		: Linéaire de réseaux visitable (> ou = à 1,5 m) et non visitable (< 150)  
    NDO 		: Nombre de DO  
    NDes 		: Nombre de dessableurs  
    NSTR		: Nombre de STR  
    NSTEU		: Nombre de STEU  
    NBEO		: Nombre de bassins enterrés et ciel ouvert  
    Nbr		: Nombre de branchements  
    NT 		: Nombre de trémie  
    NAP 		: Nombre d'arbres de pluie  
    NPI		: Nombre de puits d'infiltration  
    FPR		: Nombre de FPR  
    VPR		: Valeur patrimoniale à neuf Réseaux (Milliards d'euros)  
    VPBr		: Valeur patrimoniale à neuf Branchements (Milliards d'euros)  
    VPAP		: Valeur patrimoniale à neuf arbres de pluie (k€)  
    VPPI		: Valeur patrimoniale à neuf puits d'infiltration (M€)  
    LRAPC 	: Linéaire de reseaux avec années de pose connues & estimées  
    AMR		: Age moyen de réseaux  
    AMeR		: Age médian des réseaux  
    APSTR 	: Année de mise en place des STR  
    APSTEU	: Année de mise en place des STEU  
    LinClass	: Linéaire de réseaux en classe A, B et C  
    LDiagPrediag: Linéaire de réseaux visitables- inspection (DIAG et PREDIAG)  
    LRSFa		: Linéaires de réseaux secs courant faible / Fort  
    LinSecClass : Linéaire de réseaux secs en classe A, B et C  
    LITV		: Linéaire d'ITV  
    NISTEU	: Nombre d'inspection sur les STEU   
    NISTR		: Nombre d'inspection sur les STR  
    NITREMIES 	: Nombre d'inspection sur les trémies  
    LRSPVP	: Linéaire de réseaux sur parcelles ou voie privée  
    NPPTR		: Nombre de parcelles privées traversées par les réseaux  
    VPOGEP	: Valeur patrimoniale à neuf OGEP (Millions €)  
    VPBassins	: Valeur patrimoniale à neuf Bassins (ENT ET OUV) (Millions €)  
    VPSTR		: Valeur patrimoniale à neuf STR (Millions €)  
    VPSTEU	: Valeur patrimoniale à neuf STEU (MD€)  
    VPFPR		: Valeur patrimoniale à neuf FPR (K€)  
    VPTREM	: Valeur patrimoniale à neuf Trémies (Millions €)  
    NBR		: Nombre de bassins (ENT et OUV) récolés  
    LLI		: Linéaire de linéaire d'infiltration  
    NSteuR	: Nombre de STEU récolés  
    NSR		: Nombre de STR récolés  
    NDOR		:  
    NDesR		:  
    NTR		: Nombre de Tremies récolés  
    NFR		: Nombre de FPR récolés  
    NAPR		: Nombre de  Arbres de pluie récolés  
    LRIT		: Linéaire total d'idées de faire travaux Réseaux   
    AR		: Age de réseaux   
    ConAge	: Connaissance Année de pose  
    ConMat	: Connaissance Matériaux  
    AgeSTEU	: Age STEU  
    AgeSTR	: Age STR  
    NBCE		: Nombre de branchements connu et estimé  
    ES_NV		: ETAT DE SANTE NON VISITABLE (DONUTS)  
    ES_STEU	: ETAT DE SANTE STEU (DONUTS)  
    ES_STR	: ETAT DE SANTE STR (DONUTS)  
    ES_V		: ETAT DE SANTE Visitables (DONUTS)  
    ES_STR_EP	: ETAT DE SANTE STR_EP (DONUTS)  
    AgeBassins	: Age Bassins  
    AgeSTR_EP	: Age STR_EP  
    NNo		: Nombre de Noues (simples et composées)  
    NTr		: Nombre de Tranchée (+ tranchée de stockholm)  
    NLi		: Nombre de Linéaires d'infiltaration  
  
    EU_U  
        LRU  
        LREU  
        LEP  
        LRV  
    EP  
        LRV  
        LEP  