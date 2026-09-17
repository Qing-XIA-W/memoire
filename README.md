# Affaiblissement phonétique des occlusives en mandarin

Ce dépôt contient les scripts, données intermédiaires, résultats et ressources numériques utilisés dans le cadre du mémoire de Master 2 en Sciences du langage, parcours Analyse et Traitements Linguistiques (ATL), à l’Université d’Orléans.

Le mémoire porte sur la variation phonétique des occlusives du mandarin standard dans la parole continue, avec une attention particulière portée aux manifestations acoustiques de l’affaiblissement phonétique.

## 1. Données

Les données étudiées proviennent du corpus participatif **Lingua Libre** et concernent des productions en mandarin.

Le sous-corpus initial comprend des productions de plusieurs locuteurs. Après sélection, nettoyage et vérification des données, le sous-corpus utilisé pour les analyses statistiques comprend **1 613 occurrences d’occlusives produites par 8 locuteurs**.

Les six occlusives étudiées sont :

* /p/
* /pʰ/
* /t/
* /tʰ/
* /k/
* /kʰ/

Les analyses acoustiques portent principalement sur trois paramètres :

* la durée totale de l’occlusive ;
* le Voice Onset Time (VOT) ;
* le taux de voisement.

Les fichiers audio originaux ne sont pas inclus dans ce dépôt. Ils proviennent de Lingua Libre et les informations permettant d’identifier les données utilisées sont conservées dans les fichiers de métadonnées et de sélection du sous-corpus.

## 2. Organisation du dépôt

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
│   ├── extraction/
│   ├── génération_3_figures_descriptives.py
│   ├── génération_figure_régression_par_groupe_aspiration.py
│   ├── génération_figure_régression_vot_durée_et_proportion.py
│   ├── génération_grille_régression_par_consonne.py
│   └── .praat
│
├── results/
│   ├── LMM/
│   │    ├── Resume_Modeles_LMM.txt
│   │    └── Resume_Modeles_socio_LMM.txt
│   └── figures/
```

## 3. Scripts

Les scripts sont organisés selon les différentes étapes du traitement des données.

### `scripts/metadata/`

Scripts utilisés pour extraire et organiser les informations associées aux enregistrements et aux locuteurs.

### `scripts/textgrid/`

Scripts Praat et Python utilisés pour la lecture, la vérification et le traitement des fichiers TextGrid.

Ils comprennent notamment les scripts permettant de traiter plusieurs fichiers TextGrid de manière automatisée.

### `scripts/extraction/`

Scripts utilisés pour l’extraction des mesures acoustiques à partir des fichiers audio et des annotations.

Les principales mesures extraites sont la durée de l’occlusive, le VOT et le taux de voisement.

### `scripts/cleaning/`

Scripts utilisés pour le nettoyage et la préparation des données avant les analyses statistiques.

### `scripts/statistics/`

Scripts Python utilisés pour les analyses statistiques, notamment les **modèles linéaires à effets mixtes (LMM)**.

Les modèles prennent notamment en compte :

* la position de la consonne ;
* le statut d’aspiration ;
* le lieu d’articulation ;
* les interactions entre ces facteurs ;
* le locuteur comme effet aléatoire.

Des analyses complémentaires portent également sur certaines caractéristiques sociophonétiques des locuteurs.

### `scripts/figures/`

Scripts utilisés pour produire les figures présentées dans le mémoire à partir des données analysées.

## 4. Données intermédiaires et données analysées

Le dossier `data/subcorpus/` contient les fichiers utilisés pour définir le sous-corpus retenu pour l’analyse.

Le dossier `data/extracted/` contient les données acoustiques extraites et préparées pour les analyses statistiques.

Ces fichiers permettent de suivre les principales étapes de transformation des données, depuis la sélection du sous-corpus jusqu’aux analyses statistiques.

## 5. Résultats

Le dossier `results/` contient les résultats produits à partir des scripts d’analyse.

### `results/descriptive/`

Statistiques descriptives utilisées pour caractériser les données selon les différentes conditions phonétiques.

### `results/LMM/`

Résultats des modèles linéaires à effets mixtes utilisés dans le mémoire.

### `results/figures/`

Figures produites à partir des scripts du dossier `scripts/figures/`.

Les figures peuvent ainsi être reproduites à partir des données correspondantes et des scripts fournis dans le dépôt.

## 6. Annotation et correction manuelle

Le fichier `docs/annotation_protocol.pdf` présente les principales conventions adoptées pour la vérification et la correction manuelle des annotations.

Le protocole précise notamment les critères utilisés pour la délimitation des segments, l’identification du relâchement des occlusives, le codage du VOT et le traitement de certaines réalisations phonétiques particulières.

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

Le dépôt vise à documenter les principales étapes du traitement des données et des analyses réalisées dans le cadre du mémoire.

La chaîne de traitement peut être résumée comme suit :

```text
Lingua Libre
     ↓
Sélection des données
     ↓
Constitution du sous-corpus
     ↓
Alignement automatique
     ↓
Correction manuelle des annotations
     ↓
Extraction des mesures acoustiques
     ↓
Nettoyage et préparation des données
     ↓
Analyses statistiques
     ↓
Production des figures et des résultats
```

Les fichiers audio originaux et l’ensemble des fichiers TextGrid ne sont pas reproduits dans ce dépôt. Le dépôt contient principalement les scripts, les données structurées nécessaires aux analyses, les résultats et la documentation permettant de comprendre la chaîne de traitement.

## 9. Mémoire

Ce dépôt est associé au mémoire de Master 2 :

**Affaiblissement phonétique des occlusives en mandarin dans la parole continue — Analyse acoustique et traitement d’un corpus oral participatif**

Université d’Orléans
Master Sciences du langage — Parcours Analyse et Traitements Linguistiques (ATL)


Les conditions de réutilisation des scripts et des données sont précisées dans le fichier `LICENSE`.

