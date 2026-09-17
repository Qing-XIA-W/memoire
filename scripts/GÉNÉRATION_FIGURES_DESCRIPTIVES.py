"""
GÉNÉRATION DES FIGURES DESCRIPTIVES (BOXPLOT & BARPLOT)
==============================================================================
Description :
    Ce script génère 3 jeux de figures combinées à deux panneaux (a) et (b) :
      - Panneau (a) : Boxplot montrant la distribution globale selon l'aspiration
                      et la position syllabique (initiale vs intervocalique).
      - Panneau (b) : Barplot présentant les moyennes détaillées pour les 6 consonnes
                      occlusives cibles avec affichage des valeurs numériques.

Indicateurs traités :
    1. Voice Onset Time (VOT en ms)
    2. Durée totale d'occlusion (Durée totale en ms)
    3. Taux de voisement (Taux de voisement en %)
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# CHARGEMENT ET PRÉTRAITEMENT DES DONNÉES

# [À MODIFIER] Chemin d'accès au fichier CSV du corpus
CSV_PATH = r"X:\corpus\Souscorpus.csv"

# [À MODIFIER] Dossier d'exportation des figures générées
OUTPUT_DIR = r"X:\corpus\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH)

# Nettoyage des espaces superflus dans les chaînes de caractères
for col in ["Consonne", "Position", "Aspiration"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# Conversion numérique sécurisée des variables acoustiques
df["VOT (ms)"] = pd.to_numeric(df["VOT (ms)"], errors="coerce")

# Nettoyage et conversion du taux de voisement (suppression du symbole '%')
df["Taux_voisement_num"] = pd.to_numeric(
    df["Taux de voisement"].astype(str).str.rstrip("%"), errors="coerce"
)

# Périmètre d'étude : 6 occlusives du mandarin et 2 positions syllabiques cibles
TARGET_CONSONANTS = ["p", "pʰ", "t", "tʰ", "k", "kʰ"]
POSITIONS = ["initial", "intervocalique"]

# Filtrage du dataframe
df_plot = df[
    df["Consonne"].isin(TARGET_CONSONANTS) & df["Position"].isin(POSITIONS)
].copy()


# CONFIGURATION DU CANVAS ET DU STYLE GRAPHIQUE

sns.set_theme(style="whitegrid", font="DejaVu Sans")

# [À MODIFIER SI BESOIN] Palette de couleurs officielles pour les positions
palette = {"initial": "#2b5c8f", "intervocalique": "#d95f02"}
ASP_ORDER = ["Non-aspiré", "Aspiré"]

# Configuration des 3 figures à exporter
metrics_config = [
    {
        "col": "VOT (ms)",
        "title_prefix": "VOT (ms)",
        "fmt": ".1f",
        "output_name": "figure_A_B_VOT.png",
    },
    {
        "col": "Durée totale (ms)",
        "title_prefix": "Durée totale (ms)",
        "fmt": ".1f",
        "output_name": "figure_A_B_Duree.png",
    },
    {
        "col": "Taux_voisement_num",
        "title_prefix": "Taux de voisement (%)",
        "fmt": ".1f",
        "output_name": "figure_A_B_Voisement.png",
    },
]


# BOUCLE DE GÉNÉRATION DES FIGURES COMBINÉES (PANNEAUX a ET b)

for config in metrics_config:
    col_name = config["col"]
    title_pref = config["title_prefix"]
    fmt = config["fmt"]

    # Création d'une figure à 1 ligne et 2 colonnes
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(16, 5.5), dpi=300)

    # 【PANNEAU (a)】 Boxplot par Aspiration et Position
    # --------------------------------------------------------------------------
    sns.boxplot(
        data=df_plot,
        x="Aspiration",
        y=col_name,
        hue="Position",
        order=ASP_ORDER,
        hue_order=POSITIONS,
        palette=palette,
        ax=ax_a,
        width=0.4,
        showmeans=True,
        meanprops={
            "marker": "o",
            "markerfacecolor": "white",
            "markeredgecolor": "black",
            "markersize": "7",
        },
    )

    # Ajout du marqueur de sous-figure (a)
    ax_a.text(
        0.02, 0.95, "(a)",
        transform=ax_a.transAxes,
        fontsize=13,
        fontweight="bold",
        va="top"
    )

    ax_a.set_xlabel("Aspiration", fontsize=11)
    ax_a.set_ylabel(title_pref, fontsize=11)

    # Configuration de la légende du panneau (a)
    handles_a, _ = ax_a.get_legend_handles_labels()
    
    # [À MODIFIER SI BESOIN] Ajuster 'loc' si la légende chevauche les données
    # Options possibles : 'upper left', 'upper right', 'lower left', 'lower right'
    ax_a.legend(
        handles_a,
        ["Initiale", "Intervocalique"],
        title="Position",
        loc="upper right",
        frameon=True,
        facecolor="white",
        framealpha=0.9,
    )

    # 【PANNEAU (b)】 Barplot des moyennes par Consonne et Position
    # --------------------------------------------------------------------------
    sns.barplot(
        data=df_plot,
        x="Consonne",
        y=col_name,
        hue="Position",
        order=TARGET_CONSONANTS,
        hue_order=POSITIONS,
        palette=palette,
        ax=ax_b,
        errorbar=None,
    )

    # Ajout du marqueur de sous-figure (b)
    ax_b.text(
        0.02, 0.95, "(b)",
        transform=ax_b.transAxes,
        fontsize=13,
        fontweight="bold",
        va="top"
    )

    # Annotation des valeurs moyennes au-dessus de chaque barre
    for p in ax_b.patches:
        height = p.get_height()
        if not np.isnan(height) and height > 0:
            ax_b.annotate(
                f"{height:{fmt}}",
                (p.get_x() + p.get_width() / 2.0, height),
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                xytext=(0, 3),
                textcoords="offset points",
            )

    # Augmentation de la marge supérieure de l'axe Y pour éviter le rognage des valeurs
    current_ylim_b = ax_b.get_ylim()
    ax_b.set_ylim(0, current_ylim_b[1] * 1.15)

    ax_b.set_xlabel("Consonne", fontsize=11)
    ax_b.set_ylabel(f"Moyenne du {title_pref}", fontsize=11)

    # Configuration de la légende du panneau (b)
    handles_b, _ = ax_b.get_legend_handles_labels()
    
    # [À MODIFIER SI BESOIN] Ajuster 'loc' pour éviter de masquer les barres ou valeurs
    # 'upper right' convient aux données VOT/Durée, 'lower right' ou 'upper left' peut être utile pour le voisement
    ax_b.legend(
        handles_b,
        ["Initiale", "Intervocalique"],
        title="Position",
        loc="upper right",
        frameon=True,
        facecolor="white",
        framealpha=0.9,
    )

    # SAUVEGARDE ET EXPORTATION HAUTE RÉSOLUTION (300 DPI)

    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, config["output_name"])
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Graphique exporté avec succès : {output_path}")
    plt.close()

print("\nTraitement terminé ! Toutes les figures (VOT, Durée, Voisement) ont été générées sans titre supérieur.")
