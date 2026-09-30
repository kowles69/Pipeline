class mapping:
    pub_ref_mappings = {
        'bassin': {
            'pub_to_ref': {
                'column_mapping': {
                    'identifiantbassin': 'identifiantbassin',
                    'nombassin': 'nombassin',
                    'nature': 'nature',
                    'typebassin': 'typebassin',
                    'anneeconstruction': 'anneeconstruction',
                    'domanialite': 'domanialite',
                    'exploitant': 'exploitant',
                    'etat': 'etat',
                    'volumeexploitation': 'volumeexploitation',
                    'geom': 'geom'
                },
                'value_mapping': {
                    'nature': {
                        'Enterré': "ENT",
                        'Ciel ouvert': "OUV"
                    },
                    'typebassin': {
                        "Bassin d'infiltration": "BI",
                        "Bassin de rétention": "BR",
                        "Bassin de rétention et d'infiltration": "BRI",
                        "Bassin par filtres plantés de roseaux": "BRT"
                    },
                    'domanialite': {
                        "Département":  1,
                        "Privé":  10,
                        "Autre":  11,
                        "SYSEG":  12,
                        "SIEVA": 13,
                        "SMAAVO":  14,
                        "Commune extérieure":  15,
                        "Métropole":  2,
                        "Commune":  3,
                        "SNCF":  4,
                        "SERL":  5,
                        "Organisme HLM":  6,
                        "EDF":  7,
                        "CNR":  8,
                        "SYTRAL":  9
                    },
                    'exploitant': {
                        "Autre":  "AUT",
                        "Commune":  "COM",
                        "Département":  "DPT",
                        "Grand Lyon - Autre":  "GLA",
                        "Grand Lyon - Eau":  "GLE",
                        "Grand Lyon ' Voies rapides":  "GLVR",
                        "Privé":  "PRIV",
                    },
                    'etat': {
                        'Construit': 'CON',
                        'Projet': 'PRO'
                    }
                }
            }
        },
        'canaexp': {
            'pub_to_ref': {
                'column_mapping': {
                    "idcanaexp": "idcanaexp",
                    "longueur": "longueur",
                    "typreseau": "typreseau",
                    "typeffluen": "typeffluen",
                    "noteindigo": "noteindigo",
                    "domanialite": "domanialit",
                    "hauteur": "hauteur",
                    "annereha": "annereha",
                    "typeetude": "typeetude",
                    "geom": "geom"
                },
                'value_mapping': {
                }
            }
        },
        'canap': {
            'pub_to_ref': {
                'column_mapping': {
                    "identifiantcanap": "identifiantcanap",
                    "typeadministratifreseau": "typeadministratifreseau",
                    "typeeffluent": "typeeffluent",
                    "longueur": "longueur",
                    "domanialite": "domanialite",
                    "materiaupresume": "materiaupresume",
                    "materiau": "materiau",
                    "hauteur": "hauteur",
                    "anneepose": "anneepose",
                    "anneeposeinferieur": "anneeposeinferieur",
                    "anneeposesuperieur": "anneeposesuperieur",
                    "precisionplanimetrique": "precisionplanimetrique",
                    "geom": "geom",
                },
                'value_mapping': {
                    "typeadministratifreseau": {
                        "Eaux usées": "EU",
                        "Eaux pluviales": "EP",
                        "Unitaire": "UN",
                        "N'accepte pas de raccordement": "NO",
                        "Ruisseau": "RU"
                    },
                    "typeeffluent": {
                        "Eaux usées": "EU",
                        "Eaux pluviales": "EP",
                        "Unitaire": "UN"
                    },
                    'domanialite': {
                        "Département":  1,
                        "Privé":  10,
                        "Autre":  11,
                        "SYSEG":  12,
                        "SIEVA": 13,
                        "SMAAVO":  14,
                        "Commune extérieure":  15,
                        "Métropole":  2,
                        "Commune":  3,
                        "SNCF":  4,
                        "SERL":  5,
                        "Organisme HLM":  6,
                        "EDF":  7,
                        "CNR":  8,
                        "SYTRAL":  9
                    },
                    "materiaupresume": {
                        "Amiante cimenté": "AMCI",
                        "Autre": "AUTR",
                        "Béton avec métaux": "BTAM",
                        "Béton autre": "BTAU",
                        "Fonte": "FONT",
                        "Plastique": "PLAS",
                        "Roche": "ROCH"
                    },
                    "materiau": {
                        "Acier": "ACIE",
                        "Amiante ciment": "AMCI",
                        "Autre": "AUTR",
                        "Béton âme tôle": "BATO",
                        "Béton centrifugé armé": "BCAR",
                        "Béton coulé en fouille armé": "BCFA",
                        "Béton coulé en fouille non armé": "BCFN",
                        "Béton indéfini": "BIND",
                        "Béton LPB": "BLPB",
                        "Enduit": "ENDU",
                        "Fonte calorifugée": "FCAL",
                        "Fonte ductile": "FDUC",
                        "Fonte grise": "FGRI",
                        "Fonte": "FONT",
                        "Fonte verrouillée": "FVER",
                        "Grès": "GRES",
                                "Maçonnerie": "MACO",
                                "Polyéthylène Haute Densité": "PEHD",
                                "Polyéthylène": "PETH",
                                "Plomb": "PLOM",
                                "Polypropylène": "PP",
                                "Polyester Renforcé de fibres de Verre": "PRV",
                                "P.V.C.": "PVCL"
                    },
                    "precisionplanimetrique": {
                        "precision < 5cm": 0,
                        "5 <= precision < 10cm": 1,
                        "10 <= precision < 25cm": 2,
                        "25 <= precision < 50cm": 3,
                        "50 <= precision < 150cm": 4,
                        "150cm <= precision": 5
                    }
                }
            }
        },
        'canas': {
            'pub_to_ref': {
                'column_mapping': {
                    "identifiantcanas": "identifiantcanas",
                    "typereseau": "typereseau",
                    "precisionplanimetrique": "precisionplanimetrique",
                    "geom": "geom"
                },
                'value_mapping': {
                    "typereseau": {
                        "Eaux usées": "EU",
                        "Eaux pluviales": "EP",
                        "Unitaire": "UN"
                    },
                    "precisionplanimetrique": {
                        "precision < 5cm": 0,
                        "5 <= precision < 10cm": 1,
                        "10 <= precision < 25cm": 2,
                        "25 <= precision < 50cm": 3,
                        "50 <= precision < 150cm": 4,
                        "150cm <= precision": 5
                    }
                }
            }
        },
        'devorage': {
            'pub_to_ref': {
                'column_mapping': {
                    "identifiantdevorage": "identifiantdevorage",
                    "datecreation": "LES PROBLEMES",  # Champs dans REF pas dans PUB
                    "geom": "geom"
                },
                'value_mapping': {
                }
            }
        },
        'ogep': {
            'pub_to_ref': {
                'column_mapping': {
                    "identifiantogep": "identifiantogep",
                    "natureogep": "natureogep",
                    "length": "longueur",
                    "domanialite": "domanialite",
                    "geom": "geom"
                },
                'value_mapping': {
                    'natureogep': {
                        'Tranchée': 1,
                        'Noue': 2,
                        'Noue composée': 3,
                        'Chaussée structure réservoir': 4,
                        'Tranchée Stockholm': 5,
                        'Fossé': 6,
                        'Arbre de pluie': 7
                    }
                }
            }
        },
        'puitsf': {
            'pub_to_ref': {
                'column_mapping': {
                    "identifiantpuitsf": "identifiantpuitsf",
                    "geom": "geom"
                },
                'value_mapping': {
                }
            }
        },
        'reseausec': {
            'pub_to_ref': {
                'column_mapping': {
                    "identifiantreseausec": "identifiantreseausec",
                    "typereseausec": "typereseausec",
                    "classeprecision": "classeprecision",
                    "installation": "installation",
                    "geom": "geom"
                },
                'value_mapping': {
                    "typereseausec": {
                        'Courant faible': 'FAIBLE',
                        'Courant fort': 'FORT'
                    },
                    "installation": {
                        "Autre": "AUTR",
                        "Bassin": "BASS",
                        "Collecteur": "CANA",
                        "Dessableur": "DESS",
                        "Déversoir d'orage": "DO",
                        "Galerie technique": "GT",
                        "Linéaire d'infiltration": "LINF",
                        "Site de métrologie": "METR",
                        "Ouvrage abandonné": "OUAB",
                        "Ouvrage spécial": "OUSP",
                        "Piézomètre": "PIEZ",
                        "Site pluviomètre": "PLUV",
                        "Station de relèvement": "STAR",
                        "Station d'épuration": "STEP",
                        "Trémie": "TREM",
                        "Vanne": "VANN",
                    }
                }
            }
        },
        'stare': {
            'pub_to_ref': {
                'column_mapping': {
                    "identifiantstare": "identifiantstare",
                    "nomstare": "nomstare",
                    "numero": "numero",
                    "anneeconstruction": "anneeconstruction",
                    "geom": "geom"
                },
                'value_mapping': {
                }
            }
        },
        'steu': {
            'pub_to_ref': {
                'column_mapping': {
                    "identifiantsteu": "identifiantsteu",
                    "nomsteu": "nomsteu",
                    "anneeconstruction": "anneeconstruction",
                    "propriete": "propriete",
                    "capacite": "capacite",
                    "geom": "geom"
                },
                'value_mapping': {
                }
            }
        },
        'tremie': {
            'pub_to_ref': {
                'column_mapping': {
                    "identifianttremie": "identifianttremie",
                    "numero": "numero",
                    "anneeconstruction": "anneeconstruction",
                    "geom": "geom"
                },
                'value_mapping': {
                }
            }
        },
        'traitement': {
            'pub_to_ref': {
                'column_mapping': {
                    "identifianttraitement": "identifianttraitement",
                    "typetraitement": "typetraitement",
                    "datecreation": "LES PROBLEMES",  # Champs dans REF pas dans PUB
                    "geom": "geom"
                },
                'value_mapping': {
                }
            }
        },
        'parcelleajour': {
            'pub_to_ref': {
                'column_mapping': {
                    "idparcelle": "idparcelle",
                    "codenatureproprietaire": "codenatureproprietaire",
                    "natureproprietaire": "natureproprietaire",
                    "geom": "geom"
                },
                'value_mapping': {
                }
            }
        },
        'drain': {
            'pub_to_ref': {
                'column_mapping': {
                    "iddrain": "iddrain",
                    "datecreation": "LES PROBLEMES",  # Champs dans REF pas dans PUB
                    "geom": "geom"
                },
                'value_mapping': {
                }
            }
        }
    }
