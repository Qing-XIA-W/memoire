"""
GRILLE DE RÉGRESSION LINÉAIRE PAR PHONÈME CONSONANTIQUE (2x3)
==============================================================================

Description :
    Ce script génère deux figures sous forme de grille 2x3 (6 sous-graphiques) :
      - Grille 1 : Régression du VOT (ms) en fonction de la durée totale (ms)
                   pour chaque consonne occlusive (/p, t, k, pʰ, tʰ, kʰ/).
      - Grille 2 : Régression du taux de voisement (%) en fonction de la durée
                   totale (ms) pour les mêmes consonnes.
    Chaque sous-graphique intègre les droites de régression séparées par position
    syllabique (initiale vs intervocalique) ainsi que les coefficients de Pearson (r, p).

Instructions d'utilisation :
    1. Ajuster les chemins d'accès au fichier d'entrée (CSV_PATH) et au dossier de sortie (OUTPUT_DIR).
    2. Modifier les coordonnées (x, y) dans `ax.text()` si l'encadré de texte masque
       des points ou des courbes de régression.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import pearsonr

# CHARGEMENT ET PRÉTRAITEMENT DES DONNÉES

# [À MODIFIER] Chemin d'accès au fichier CSV du corpus
CSV_PATH = r"X:\corpus\Souscorpus.csv"

# [À MODIFIER] Dossier de destination pour l'exportation des figures
OUTPUT_DIR = r"X:\corpus\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH)

# Nettoyage des espaces superflus dans les variables textuelles
for col in ["Consonne", "Position"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# Conversion numérique sécurisée des variables acoustiques (Durée déjà en ms)
df["Durée totale (ms)"] = pd.to_numeric(df["Durée totale (ms)"], errors="coerce")
df["VOT (ms)"] = pd.to_numeric(df["VOT (ms)"], errors="coerce")
df["Taux_voisement_num"] = pd.to_numeric(
    df["Taux de voisement"].astype(str).str.rstrip("%"), errors="coerce"
)

POSITIONS = ["initial", "intervocalique"]

# Disposition de la grille 2x3 : ligne 1 = non-aspirées, ligne 2 = aspirées
CONSONANTS_GRID = [
    ["p", "t", "k"],
    ["pʰ", "tʰ", "kʰ"]
]

df_plot = df[
    df["Consonne"].isin(["p", "pʰ", "t", "tʰ", "k", "kʰ"])
    & df["Position"].isin(POSITIONS)
].copy()

# CONFIGURATION DU CANVAS ET DES TÂCHES DE RÉGRESSION

sns.set_theme(style="whitegrid", font="DejaVu Sans")

# [À MODIFIER SI BESOIN] Palette de couleurs pour les positions syllabiques
color_map = {"initial": "#2b5c8f", "intervocalique": "#d95f02"}

regression_tasks = [
    {
        "y_col": "VOT (ms)",
        "y_label": "VOT (ms)",
        "output_filename": "regression_VOT_vs_Duree_with_stats.png",
        "ylim": None,
    },
    {
        "y_col": "Taux_voisement_num",
        "y_label": "Taux de voisement (%)",
        "output_filename": "regression_Voisement_vs_Duree_with_stats.png",
        "ylim": (0, 105),  # Plafond strict à 105% pour éviter les valeurs négatives
    },
]


# BOUCLE DE GÉNÉRATION DES GRILLES DE RÉGRESSION (2 x 3)

for task in regression_tasks:
    y_col = task["y_col"]
    y_label = task["y_label"]
    output_filename = task["output_filename"]
    ylim = task["ylim"]

    fig, axes = plt.subplots(2, 3, figsize=(15, 8.2), dpi=300, sharex=True, sharey=True)

    for row_idx in range(2):
        for col_idx in range(3):
            ax = axes[row_idx, col_idx]
            consonne = CONSONANTS_GRID[row_idx][col_idx]

            sub_df = df_plot[df_plot["Consonne"] == consonne].copy()
            stats_list = []

            # Calcul des régressions séparées pour 'initiale' et 'intervocalique'
            for pos in POSITIONS:
                pos_df = sub_df[sub_df["Position"] == pos].dropna(
                    subset=["Durée totale (ms)", y_col]
                )

                if len(pos_df) > 1:
                    # Calcul du coefficient de Pearson (r et p-value)
                    r_val, p_val = pearsonr(pos_df["Durée totale (ms)"], pos_df[y_col])
                    p_str = "p<0.001" if p_val < 0.001 else f"p={p_val:.3f}"
                    pos_tag = "Init" if pos == "initial" else "Inter"
                    stats_list.append(f"{pos_tag}: r={r_val:.2f}, {p_str}")

                    # Tracé des points de dispersion et de la droite de régression
                    sns.regplot(
                        data=pos_df,
                        x="Durée totale (ms)",
                        y=y_col,
                        ax=ax,
                        color=color_map[pos],
                        label="Initiale" if pos == "initial" else "Intervocalique",
                        scatter_kws={"s": 25, "alpha": 0.6},
                        line_kws={"linewidth": 2},
                        ci=95,
                    )

            # Formatage du texte des statistiques et du nom du phonème
            stats_text = "\n".join(stats_list)
            box_text = f"/{consonne}/\n{stats_text}" if stats_text else f"/{consonne}/"

            # [À MODIFIER SI BESOIN] Ajuster les coordonnées (ex: x=0.90, y=0.65)
            # pour déplacer l'encadré s'il masque les données du sous-graphique
            ax.text(
                0.90, 0.65, box_text,
                transform=ax.transAxes,
                fontsize=9,
                fontweight="bold",
                horizontalalignment="right",
                verticalalignment="bottom",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.85, edgecolor="gray")
            )

            ax.set_xlabel("Durée totale (ms)", fontsize=10)
            ax.set_ylabel(y_label, fontsize=10)

            if ylim:
                ax.set_ylim(ylim)

            ax.grid(True, linestyle="--", alpha=0.5)

    # Configuration de la légende globale unifiée (partagée par l'ensemble des 6 sous-graphiques)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    unique_legend = dict(zip(labels, handles))
    
    # [À MODIFIER SI BESOIN] Ajuster bbox_to_anchor si la légende globale chevauche le sous-graphique supérieur droit
    fig.legend(
        unique_legend.values(),
        unique_legend.keys(),
        loc="upper right",
        bbox_to_anchor=(0.99, 0.99),
        title="Position",
        frameon=True,
        facecolor="white",
        fontsize=9.5,
    )

    # SAUVEGARDE ET EXPORTATION HAUTE RÉSOLUTION (300 DPI)
    plt.tight_layout()
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    # Rognage automatique des espaces blancs supérieurs et périphériques
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Grille de régression exportée avec succès : {output_path}")
    plt.close()

print("\nTraitement terminé ! Les deux grilles 2x3 de régression par consonne ont été générées.")
