"""
SCRIPT PYTHON : RÉGRESSION LINÉAIRE GROUPÉE PAR TYPE D'ASPIRATION
==============================================================================

Description :
    Ce script génère des figures de régression linéaire à deux panneaux (1 x 2) :
      - Comparaison entre la durée totale (ms) et le VOT (ms) ou le taux de 
        voisement (%) pour deux groupes distincts : Non-aspiré vs Aspiré.
      - Traçage automatique des droites de régression par position syllabique 
        (initiale vs intervocalique) avec affichage des coefficients r et p.

Instructions d'utilisation :
    1. Adapter les chemins d'accès au fichier d'entrée (CSV_PATH) et au dossier de sortie (OUTPUT_DIR).
    2. Ajuster les coordonnées de l'encadré des statistiques (x, y) dans `ax.text()` 
       si le texte chevauche les points ou les droites de régression.
==============================================================================
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

# [À MODIFIER] Dossier de destination pour l'exportation des images
OUTPUT_DIR = r"X:\corpus\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH)

# Nettoyage des espaces superflus dans les variables textuelles
for col in ["Consonne", "Position", "Aspiration"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# Conversions numériques sécurisées
df["Durée totale (ms)"] = pd.to_numeric(df["Durée totale (ms)"], errors="coerce")
df["VOT (ms)"] = pd.to_numeric(df["VOT (ms)"], errors="coerce")
df["Taux_voisement_num"] = pd.to_numeric(
    df["Taux de voisement"].astype(str).str.rstrip("%"), errors="coerce"
)

# Variables d'analyse et filtrage des consonnes cibles
POSITIONS = ["initial", "intervocalique"]
TARGET_CONSONANTS = ["p", "pʰ", "t", "tʰ", "k", "kʰ"]

df_plot = df[
    df["Consonne"].isin(TARGET_CONSONANTS) & df["Position"].isin(POSITIONS)
].copy()


# CONFIGURATION DU CANVAS ET DES TÂCHES DE RÉGRESSION
sns.set_theme(style="whitegrid", font="DejaVu Sans")

# [À MODIFIER SI BESOIN] Palette de couleurs pour les positions syllabiques
color_map = {"initial": "#2b5c8f", "intervocalique": "#d95f02"}
ASP_GROUPS = ["Non-aspiré", "Aspiré"]

regression_tasks = [
    {
        "y_col": "VOT (ms)",
        "y_label": "VOT (ms)",
        "output_filename": "regression_Aspirated_NonAspirated_VOT.png",
        "ylim": None,
    },
    {
        "y_col": "Taux_voisement_num",
        "y_label": "Taux de voisement (%)",
        "output_filename": "regression_Aspirated_NonAspirated_Voisement.png",
        "ylim": (0, 105),  # Limite stricte [0, 105] pour le voisement
    },
]


# BOUCLE DE TRACÉ DES GRAPHIQUES DE RÉGRESSION (PANNEAUX 1 x 2)
for task in regression_tasks:
    y_col = task["y_col"]
    y_label = task["y_label"]
    output_filename = task["output_filename"]
    ylim = task["ylim"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.0), dpi=300, sharex=True, sharey=True)

    for idx, asp_type in enumerate(ASP_GROUPS):
        ax = axes[idx]
        sub_df = df_plot[df_plot["Aspiration"] == asp_type].copy()

        stats_titles = []

        # Calcul des régressions séparées par position syllabique
        for pos in POSITIONS:
            pos_df = sub_df[sub_df["Position"] == pos].dropna(
                subset=["Durée totale (ms)", y_col]
            )

            if len(pos_df) > 1:
                # Calcul du coefficient de Pearson (r et p-value)
                r_val, p_val = pearsonr(pos_df["Durée totale (ms)"], pos_df[y_col])
                p_str = "p < 0.001" if p_val < 0.001 else f"p = {p_val:.3f}"
                pos_name = "Init" if pos == "initial" else "Inter"
                stats_titles.append(f"{pos_name}: r = {r_val:.2f}, {p_str}")

                # Tracé des points et de la droite de régression
                sns.regplot(
                    data=pos_df,
                    x="Durée totale (ms)",
                    y=y_col,
                    ax=ax,
                    color=color_map[pos],
                    label="Initiale" if pos == "initial" else "Intervocalique",
                    scatter_kws={"s": 30, "alpha": 0.6},
                    line_kws={"linewidth": 2},
                    ci=95,
                )

        # Formatage du texte d'information statistique
        stats_text = "\n".join(stats_titles)
        box_text = f"Groupe : {asp_type}\n{stats_text}" if stats_text else f"Groupe : {asp_type}"

        # [À MODIFIER SI BESOIN] Ajuster x et y (ex: x=0.97, y=0.22) pour déplacer le bloc de texte
        # si celui-ci masque des données ou des droites de régression.
        ax.text(
            0.97, 0.22, box_text,
            transform=ax.transAxes,
            fontsize=8.5,
            fontweight="bold",
            horizontalalignment="right",
            verticalalignment="bottom",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", alpha=0.85, edgecolor="gray")
        )

        ax.set_xlabel("Durée totale (ms)", fontsize=11)
        ax.set_ylabel(y_label, fontsize=11)

        if ylim:
            ax.set_ylim(ylim)

        ax.grid(True, linestyle="--", alpha=0.5)

    # Configuration de la légende globale unifiée (partagée par les deux sous-graphiques)
    handles, labels = axes[0].get_legend_handles_labels()
    unique_legend = dict(zip(labels, handles))
    
    # [À MODIFIER SI BESOIN] Ajuster bbox_to_anchor si la légende chevauche le graphique de droite
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
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Graphique de régression exporté avec succès : {output_path}")
    plt.close()

print("\nTraitement terminé ! Toutes les figures groupées par aspiration ont été régénérées.")
