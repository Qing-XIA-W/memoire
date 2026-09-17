# Affaiblissement phonétique des occlusives en mandarin

Ce dépôt contient les scripts, les données intermédiaires, les résultats et les ressources numériques utilisés dans le cadre du mémoire de Master 2 en Sciences du langage, parcours Analyse et Traitements Linguistiques (ATL), à l’Université d’Orléans.

Le mémoire porte sur la variation phonétique des occlusives du mandarin standard dans la parole continue, avec une attention particulière portée aux manifestations acoustiques de l’affaiblissement phonétique.

## 1. Organisation du dépôt

```text
memoire/
│
├── README.md
│
├── data/
│   ├── Souscorpus.csv
│   ├── corpus_consonants_extraction.csv
│   ├── Metadata.xlsx
│   └── metapp.xlsx
│
├── scripts/
│   ├── ajustement_modeles_lmm_consonnes.py
│   ├── ajustement_modeles_lmm_sociolinguistiques.py
│   ├── extraction_automatisée_des_paramètres_consonnes.py
│   ├── génération_3_figures_descriptives.py
│   ├── génération_figure_régression_par_groupe_aspiration.py
│   ├── génération_figure_régression_vot_durée_et_proportion.py
│   ├── génération_grille_régression_par_consonne.py
│   └── .praat
│
├── results/
    ├── LMM/
    │   ├── Resume_Modeles_LMM.txt
    │   └── Resume_Modeles_socio_LMM.txt
    │
    └── figures/
```

## 2. Données

Le dossier `data/` contient les principaux fichiers de données utilisés au cours de la constitution du sous-corpus et des analyses.

### `corpus_consonants_extraction.csv`

Ce fichier contient les résultats de l’extraction automatique des paramètres acoustiques à partir du corpus traité.

Il comprend au total **10 847 occurrences**.

Les principales informations acoustiques utilisées dans l’étude comprennent notamment la durée de la consonne, le VOT et le taux de voisement.

À ce stade du traitement, les valeurs de VOT n’ont pas fait l’objet d’une vérification manuelle systématique.

### `Souscorpus.csv`

Ce fichier correspond au sous-corpus finalement retenu pour les analyses statistiques.

Il a été constitué à partir du fichier `corpus_consonants_extraction.csv` après sélection et nettoyage des occurrences. Il contient **1 613 occurrences**.

Les valeurs de VOT présentes dans ce fichier ont fait l’objet d’une **vérification manuelle** afin de contrôler l’identification du relâchement de l’occlusive et du début du voisement.

Ce fichier constitue donc la principale table de données utilisée pour les analyses statistiques présentées dans le mémoire.

### `Metadata.xlsx`

Ce fichier de métadonnées a été constitué manuellement à partir des informations disponibles pour les locuteurs.

Il contient notamment les variables suivantes :

* `ID locuteur`
* `Genre`
* `Lieu de résidence`
* `Nb d'audios`
* `Langue maternelle`
* `Autre Langue (Niveau)`

Ces informations permettent de documenter les caractéristiques générales des locuteurs du corpus et d’examiner certaines dimensions sociophonétiques.

### `metapp.xlsx`

Ce fichier constitue une version simplifiée des métadonnées, préparée spécifiquement pour être intégrée au fichier `corpus_consonants_extraction.csv`.

Il contient uniquement les trois premières informations nécessaires à cette opération :

* `ID locuteur`
* `Genre`
* `Lieu de résidence`

Il s’agit donc d’un fichier intermédiaire destiné principalement à la préparation des données pour les analyses.

## 3. Scripts

Le dossier `scripts/` contient les scripts utilisés pour les différentes étapes du traitement et de l’analyse des données.

### Extraction des paramètres acoustiques

`extraction_automatisée_des_paramètres_consonnes.py`

Ce script est utilisé pour l’extraction automatisée des principaux paramètres acoustiques des consonnes à partir des fichiers audio et des annotations.

Il permet notamment de produire les données acoustiques regroupées dans `corpus_consonants_extraction.csv`.

### Traitement des fichiers Praat / TextGrid

`.praat`

Ce script Praat est utilisé pour le traitement et la lecture de plusieurs fichiers TextGrid dans le cadre de la vérification et du traitement des annotations.

### Analyses statistiques

`ajustement_modeles_lmm_consonnes.py`

Ce script réalise les modèles linéaires à effets mixtes utilisés pour analyser les paramètres acoustiques des occlusives en fonction des variables phonétiques retenues dans l’étude.

Les analyses prennent notamment en compte :

* la position de la consonne ;
* le statut d’aspiration ;
* le lieu d’articulation ;
* les interactions entre ces facteurs ;
* le locuteur comme effet aléatoire.

`ajustement_modeles_lmm_sociolinguistiques.py`

Ce script réalise les modèles linéaires à effets mixtes utilisés pour examiner les associations entre les paramètres acoustiques et certaines caractéristiques sociophonétiques des locuteurs, notamment le genre et le lieu de résidence déclaré.

### Production des figures

Les scripts suivants sont utilisés pour produire les figures et visualisations présentées dans le mémoire :

* `génération_3_figures_descriptives.py`
* `génération_figure_régression_par_groupe_aspiration.py`
* `génération_figure_régression_vot_durée_et_proportion.py`
* `génération_grille_régression_par_consonne.py`

Ces scripts permettent de produire différentes représentations descriptives et graphiques des relations entre les paramètres acoustiques étudiés.

Les figures présentes dans `results/figures/` correspondent aux figures retenues pour la présentation des résultats dans le mémoire. Toutes les sorties graphiques produites au cours de l’exploration des données ne sont pas nécessairement incluses dans ce dossier.

## 4. Résultats

Le dossier `results/` contient les principaux résultats utilisés dans le mémoire.

### `results/figures/`

Ce dossier contient les principales figures utilisées dans le mémoire.

Il ne contient pas nécessairement l’ensemble des graphiques produits au cours de l’exploration et de l’analyse des données. Les scripts de génération des figures sont toutefois fournis dans le dossier `scripts/`, afin de documenter les procédures utilisées pour leur production.

### `results/LMM/`

Ce dossier contient les résumés des modèles linéaires à effets mixtes :

* `Resume_Modeles_LMM.txt` : résultats des modèles portant sur les caractéristiques phonétiques des occlusives ;
* `Resume_Modeles_socio_LMM.txt` : résultats des modèles portant sur les caractéristiques sociophonétiques des locuteurs.

Les scripts correspondants sont disponibles dans le dossier `scripts/`, ce qui permet de relier les résultats présentés aux procédures statistiques utilisées.

## 5. Chaîne générale de traitement

La constitution des données analysées et la réalisation des analyses peuvent être résumées comme suit :

```text
Corpus et métadonnées Lingua Libre
                ↓
       Extraction automatique
                ↓
corpus_consonants_extraction.csv
       (10 847 occurrences)
                ↓
      Sélection et nettoyage
                ↓
         Souscorpus.csv
       (1 613 occurrences)
                ↓
       Vérification manuelle
             du VOT
                ↓
     Analyses statistiques
                ↓
      ┌─────────┴─────────┐
      ↓                   ↓
    Figures              LMM
      ↓                   ↓
   results/figures      results/LMM    
```

## 6. Annotation et vérification manuelle

Les données ont été alignées automatiquement puis vérifiées et corrigées manuellement lorsque cela était nécessaire.

Une attention particulière a été portée à l’identification des frontières segmentales et à la mesure du VOT. Les valeurs de VOT du sous-corpus final ont notamment été vérifiées manuellement afin de contrôler l’identification du relâchement de l’occlusive et du début du voisement.

Les conventions d’annotation et de correction utilisées dans le cadre du mémoire sont décrites dans le protocole d’annotation associé au travail.

## 7. Outils logiciels et bibliothèques Python utilisés pour le traitement et l'analyse des données

Les analyses ont été réalisées à l’aide de plusieurs logiciels et bibliothèques, notamment :

| Outil | Version | Fonction |
| :--- | :--- | :--- |
| **Praat** | 6.4.44 | Analyse acoustique, vérification manuelle et annotation des limites phonématiques |
| **SPPAS** | 4.31 | Alignement phonétique automatique et segmentation temporelle des corpus |
| **MFA** | 3.0.0 | Alignement automatique texte-parole fondé sur des modèles acoustiques probabilistes |
| **Python** | 3.12.10 | Langage de programmation principal pour le traitement des données et l'analyse statistique |
| **pandas** | 3.0.1 | Manipulation de données structurées, nettoyage du sous-corpus et agrégation des variables |
| **NumPy** | 2.4.3 | Calcul matriciel et opérations mathématiques élémentaires |
| **Parselmouth** | 0.4.7 | Interface Python avec le moteur de Praat pour l'extraction automatisée des paramètres acoustiques (F0, VOT, intensité) |
| **praatio** | 6.2.2 | Lecture, modification et écriture programmatique des fichiers d'annotation TextGrid |
| **SciPy** | 1.18.0 | Analyses statistiques inférentielles (tests de Pearson, tests t) et modules scientifiques (`scipy.stats`) |
| **statsmodels** | 0.14.6 | Modélisation statistique avancée (régression OLS avec erreurs-types robustes HC3/Cluster, Modèles Linéaires Mixtes -- LMM) |
| **Matplotlib** | 3.11.0 | Génération et configuration fine des graphiques scientifiques (nuages de points, régressions, visualisations d'alignement) |
| **Seaborn** | 0.13.2 | Visualisation statistique de haut niveau (boxplots, barplots, régressions multi-groupes) |
| **TextGrid** | 1.6.1 | Manipulation simple et parsing orienté objet des fichiers TextGrid de Praat (lecture/écriture des tiers et des intervalles) |

## 8. Reproductibilité

Ce dépôt vise à documenter les principales étapes du traitement des données et des analyses réalisées dans le cadre du mémoire.

Les fichiers de données et les scripts permettent notamment de distinguer :

1. les données issues de l’extraction automatique ;
2. le sous-corpus sélectionné pour les analyses ;
3. les mesures de VOT après vérification manuelle ;
4. les procédures statistiques utilisées ;
5. les scripts de production des figures.

Les fichiers audio originaux et l’ensemble des fichiers TextGrid ne sont pas inclus dans ce dépôt. Les données originales proviennent de Lingua Libre.

## 9. Mémoire

Ce dépôt est associé au mémoire de Master 2 :

**Affaiblissement phonétique des occlusives en mandarin dans la parole continue — Analyse acoustique et traitement d’un corpus oral participatif**

Université d’Orléans
Master Sciences du langage — Parcours Analyse et Traitements Linguistiques (ATL)
