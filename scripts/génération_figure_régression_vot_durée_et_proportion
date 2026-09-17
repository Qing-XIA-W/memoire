"""
RÉGRESSION VOT/DURÉE ET PROPORTION DU VOT PAR PHONÈME
==============================================================================

Description :
    Ce script produit une figure scientifique composée de deux panneaux (a) et (b) :
      - Panneau (a) : Nuage de points et droites de régression linéaire entre le VOT (ms)
                      et la durée totale d'occlusion (ms), ventilés par position syllabique
                      (initiale vs intervocalique) avec calcul des coefficients de Pearson (r, p).
      - Panneau (b) : Diagramme en barres représentant le pourcentage moyen du VOT
                      par rapport à la durée totale pour chaque consonne occlusive.

Utilisation :
    1. Adapter le chemin du fichier CSV d'entrée (`CSV_PATH`) et du dossier de sortie (`OUTPUT_DIR`).
    2. Ajuster l'emplacement de l'encadré statistique ou de la légende (`loc=...`) si besoin.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import pearsonr

# CHARGEMENT ET PRÉTRAITEMENT DES DONNÉES
# ==============================================================================
# [À MODIFIER] Chemin vers le fichier CSV contenant le corpus
CSV_PATH = r"X:\corpus\Souscorpus.csv"

# [À MODIFIER] Dossier de destination pour l'exportation des images
OUTPUT_DIR = r"X:\corpus\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_PATH)

# Nettoyage des espaces superflus dans les variables textuelles
for col in ["Consonne", "Position"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# Conversion de la durée totale en millisecondes (ms)
if "Durée totale (s)" in df.columns:
    df["Durée totale (ms)"] = (
        pd.to_numeric(df["Durée totale (s)"], errors="coerce") * 1000.0
    )
else:
    df["Durée totale (ms)"] = pd.to_numeric(
        df["Durée totale (ms)"], errors="coerce"
    )

# Conversion numérique du VOT (ms)
df["VOT (ms)"] = pd.to_numeric(df["VOT (ms)"], errors="coerce")

# Calcul de la proportion du VOT dans la durée totale d'occlusion (%)
df["VOT_Ratio (%)"] = (df["VOT (ms)"] / df["Durée totale (ms)"]) * 100.0

# Définition des consonnes et des positions cibles
TARGET_CONSONANTS = ["p", "pʰ", "t", "tʰ", "k", "kʰ"]
POSITIONS = ["initial", "intervocalique"]

# Filtrage du jeu de données (suppression des valeurs manquantes pour le VOT et la Durée)
df_plot = df[
    df["Consonne"].isin(TARGET_CONSONANTS) & df["Position"].isin(POSITIONS)
].dropna(subset=["Durée totale (ms)", "VOT (ms)"]).copy()


# CONFIGURATION DU CANVAS ET DU STYLE GRAPHIQUE

sns.set_theme(style="whitegrid", font="DejaVu Sans")

# [À MODIFIER SI BESOIN] Palette de couleurs pour les positions syllabiques
palette = {"initial": "#2b5c8f", "intervocalique": "#d95f02"}

# Initialisation d'une figure à 1 ligne et 2 colonnes (hauteur 5.2 pour éviter les vides supérieurs)
fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(16, 5.2), dpi=300)


# 【PANNEAU (a)】 RÉGRESSION LINÉAIRE : VOT (ms) vs. DURÉE TOTALE (ms)

stats_text = []

for pos in POSITIONS:
    pos_df = df_plot[df_plot["Position"] == pos]
    
    if len(pos_df) > 1:
        # Calcul de la corrélation de Pearson (r et p-value)
        r_val, p_val = pearsonr(pos_df["Durée totale (ms)"], pos_df["VOT (ms)"])
        p_str = "p < 0.001" if p_val < 0.001 else f"p = {p_val:.3f}"
        pos_name = "Init" if pos == "initial" else "Inter"
        stats_text.append(f"{pos_name}: r = {r_val:.2f}, {p_str}")

        # Tracé du nuage de points et de la droite de régression
        sns.regplot(
            data=pos_df,
            x="Durée totale (ms)",
            y="VOT (ms)",
            ax=ax_a,
            color=palette[pos],
            label="Initiale" if pos == "initial" else "Intervocalique",
            scatter_kws={"s": 25, "alpha": 0.55},
            line_kws={"linewidth": 2},
            ci=95,
        )

# Ajout du marqueur de sous-figure (a)
ax_a.text(
    0.02, 0.95, "(a)",
    transform=ax_a.transAxes,
    fontsize=13,
    fontweight="bold",
    va="top"
)

# [À MODIFIER SI BESOIN] Encadré des statistiques (y=0.86 évite le chevauchement avec '(a)')
stats_display = " | ".join(stats_text)
ax_a.text(
    0.02, 0.86, stats_display,
    transform=ax_a.transAxes,
    fontsize=9,
    verticalalignment="top",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.85, edgecolor="gray")
)

ax_a.set_xlabel("Durée totale (ms)", fontsize=11)
ax_a.set_ylabel("VOT (ms)", fontsize=11)

# [À MODIFIER SI BESOIN] Position de la légende du panneau (a) ('lower right', 'upper left', etc.)
ax_a.legend(title="Position", loc="lower right", frameon=True, facecolor="white")

 
# 【PANNEAU (b)】 BARPLOT : PROPORTION DU VOT / DURÉE TOTALE (%)

sns.barplot(
    data=df_plot,
    x="Consonne",
    y="VOT_Ratio (%)",
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

# Annotations textuelles des valeurs moyennes en % au-dessus des barres
for p in ax_b.patches:
    height = p.get_height()
    if not np.isnan(height) and height > 0:
        ax_b.annotate(
            f"{height:.1f}%",
            (p.get_x() + p.get_width() / 2.0, height),
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            xytext=(0, 3),
            textcoords="offset points",
        )

# Extension du plafond de l'axe Y pour éviter que les étiquettes dépassent du cadre
current_ylim_b = ax_b.get_ylim()
ax_b.set_ylim(0, current_ylim_b[1] * 1.15)

ax_b.set_xlabel("Consonne", fontsize=11)
ax_b.set_ylabel("VOT / Durée totale (%)", fontsize=11)

# [À MODIFIER SI BESOIN] Position de la légende du panneau (b)
handles_b, labels_b = ax_b.get_legend_handles_labels()
ax_b.legend(
    handles_b,
    ["Initiale", "Intervocalique"],
    title="Position",
    loc="lower right",
    frameon=True,
    facecolor="white",
    framealpha=0.9,
)

# EXPORTATION ET SAUVEGARDE

plt.tight_layout()
output_img_path = os.path.join(OUTPUT_DIR, "figure_A_B_VOT_Ratio_Duree.png")

# Utilization de bbox_inches='tight' pour éliminer les marges blanches inutiles
plt.savefig(output_img_path, dpi=300, bbox_inches="tight")
print(f"Graphique exporté avec succès vers : {output_img_path}")
plt.close()
