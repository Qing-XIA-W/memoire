"""
AJUSTEMENT ET EXPORTATION DES MODÈLES LINÉAIRES MIXTES (LMM)
==============================================================================
Description :
    Ce script prépare les données acoustiques (transformations logarithmiques et logit),
    fixe explicitement les niveaux de référence d'origine (baseline : initial, Aspiré, dental)
    au niveau des catégories pandas, puis ajuste 9 modèles LMM avec l'effet aléatoire (1 | Locuteur).

    Les résumés complets des modèles sont enregistrés dans un fichier TXT en français.
==============================================================================
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# Ignorer les avertissements de convergence secondaires
warnings.filterwarnings("ignore")

# CHEMINS D'ACCÈS ET CONFIGURATION

# [À MODIFIER] Chemin d'accès au fichier CSV du corpus
CSV_PATH = r"X:\corpus\Souscorpus.csv"

# [À MODIFIER] Chemin du fichier texte de sortie
OUTPUT_TXT = r"X:\corpus\output\Resume_Modeles_LMM.txt"

os.makedirs(os.path.dirname(OUTPUT_TXT), exist_ok=True)
df = pd.read_csv(CSV_PATH)

# NORMALISATION ET PRÉTRAITEMENT DES DONNÉES

# Harmonisation des nommages de colonnes 
rename_dict = {
    "Durée totale (ms)": "Duree_ms",
    "Taux de voisement": "Taux_voisement_raw",
    "VOT (ms)": "VOT_ms",
    "Aspiration": "Aspiration",
    "Position": "Position",
    "Lieu d'articulation": "Lieu_articulation",
}
df = df.rename(columns=rename_dict)

# Nettoyage des espaces pour les variables catégorielles
for cat_col in ["Position", "Aspiration", "Lieu_articulation", "Locuteur"]:
    if cat_col in df.columns:
        df[cat_col] = df[cat_col].astype(str).str.strip()

# Conversion numérique des variables acoustiques
df["Duree_ms"] = pd.to_numeric(df["Duree_ms"], errors="coerce")
df["VOT_ms"] = pd.to_numeric(df["VOT_ms"], errors="coerce")

# (1) Log_Duree = ln(Duree_ms)
df["Log_Duree"] = np.log(df["Duree_ms"])

# (2) Log_VOT = ln(VOT_ms + 1)
df["Log_VOT"] = np.log(df["VOT_ms"] + 1.0)

# (3) Transformation Logit Squeezed pour le Taux de voisement
df["Voisement_num"] = pd.to_numeric(
    df["Taux_voisement_raw"].astype(str).str.rstrip("%"), errors="coerce"
)
p_raw = df["Voisement_num"] / 100.0
p_raw = p_raw.clip(lower=0.0, upper=1.0)

N = len(df)
p_squeezed = (p_raw * (N - 1) + 0.5) / N
df["Logit_Voisement"] = np.log(p_squeezed / (1.0 - p_squeezed))

#  FIXATION RIGOUREUSE DES NIVEAUX DE RÉFÉRENCE (BASELINE D'ORIGINE)

# 1. Position -> baseline = 'initial'
pos_categories = ["initial"] + [c for c in df["Position"].unique() if c != "initial" and pd.notna(c)]
df["Position"] = pd.Categorical(df["Position"], categories=pos_categories, ordered=False)

# 2. Aspiration -> baseline = 'Aspiré' (pour obtenir T.Non-aspiré dans l'output)
asp_categories = ["Aspiré"] + [c for c in df["Aspiration"].unique() if c != "Aspiré" and pd.notna(c)]
df["Aspiration"] = pd.Categorical(df["Aspiration"], categories=asp_categories, ordered=False)

# 3. Lieu d'articulation -> baseline = 'dental' (pour obtenir T.labial, T.vélaire, etc.)
lieu_categories = ["dental"] + [c for c in df["Lieu_articulation"].unique() if c != "dental" and pd.notna(c)]
df["Lieu_articulation"] = pd.Categorical(df["Lieu_articulation"], categories=lieu_categories, ordered=False)

# DÉFINITION DES 9 MODÈLES LMM
# ==============================================================================
formulas = {
    # Partie 1 : Effets principaux et interactions d'ordre 2
    "Modèle 1 (Effets principaux & Interactions d'ordre 2 - Log_Durée)": (
        "Log_Duree ~ (Position + Aspiration + Lieu_articulation)**2"
    ),
    "Modèle 2 (Effets principaux & Interactions d'ordre 2 - Log_VOT)": (
        "Log_VOT ~ (Position + Aspiration + Lieu_articulation)**2"
    ),
    "Modèle 3 (Effets principaux & Interactions d'ordre 2 - Logit_Voisement)": (
        "Logit_Voisement ~ (Position + Aspiration + Lieu_articulation)**2"
    ),
    # Partie 2 : Relations de modulation entre Durée et VOT
    "Modèle 4 (Relation Durée-VOT de base)": "Log_VOT ~ Duree_ms",
    "Modèle 5 (Relation Durée-VOT * Position)": "Log_VOT ~ Duree_ms * Position",
    "Modèle 6 (Relation Durée-VOT * Aspiration)": "Log_VOT ~ Duree_ms * Aspiration",
    # Partie 3 : Relations de modulation entre Durée et Taux de voisement
    "Modèle 7 (Relation Durée-Voisement de base)": "Logit_Voisement ~ Duree_ms",
    "Modèle 8 (Relation Durée-Voisement * Position)": "Logit_Voisement ~ Duree_ms * Position",
    "Modèle 9 (Relation Durée-Voisement * Aspiration)": "Logit_Voisement ~ Duree_ms * Aspiration",
}

#  AJUSTEMENT ET EXPORTATION EN FRANÇAIS

print("Ajustement des 9 modèles LMM en cours...")
print(f"Les résultats seront exportés vers le fichier texte :\n{OUTPUT_TXT}\n")

with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
    original_stdout = sys.stdout
    sys.stdout = f

    print("=" * 80)
    print("   RÉSUMÉ DES RÉSULTATS D'ANALYSE STATISTIQUE PAR MODÈLES LMM (9 MODÈLES)")
    print("=" * 80)
    print(f"Nombre total d'observations dans le jeu de données : {len(df)}")
    print(f"Nombre total de locuteurs (Locuteur) : {df['Locuteur'].nunique()}")
    print("-" * 80)
    print("Niveaux de référence (Baseline) appliqués :")
    print(f"  - Position            : '{df['Position'].cat.categories[0]}'")
    print(f"  - Aspiration          : '{df['Aspiration'].cat.categories[0]}'")
    print(f"  - Lieu d'articulation : '{df['Lieu_articulation'].cat.categories[0]}'")
    print("=" * 80 + "\n\n")

    for name, formula in formulas.items():
        print("=" * 80)
        print(f" Ajustement du modèle : {name}")
        print(f" Formule syntaxique : {formula}")
        print("=" * 80)

        # Extraction des variables présentes dans la formule
        vars_in_formula = [
            v.strip()
            for v in formula.replace("~", "+")
            .replace("*", "+")
            .replace("(", "")
            .replace(")", "")
            .split("+")
        ]
        vars_in_formula = [v for v in vars_in_formula if v in df.columns]
        required_cols = list(set(["Locuteur"] + vars_in_formula))

        is_vot_model = "Log_VOT" in formula or "VOT_ms" in formula
        df_clean = df.dropna(subset=required_cols).copy().reset_index(drop=True)

        if is_vot_model:
            print(
                f" Effectif valide (après suppression des NA VOT) : {len(df_clean)} / {len(df)}"
            )
        else:
            print(f" Effectif valide : {len(df_clean)}")

        try:
            # Modèle LMM avec effet aléatoire d'interception par locuteur (1 | Locuteur)
            model = smf.mixedlm(formula, data=df_clean, groups=df_clean["Locuteur"])
            result = model.fit(reml=True)
            print(result.summary())
        except Exception as e:
            print(f"[ERREUR] Échec de l'ajustement du modèle {name} : {e}")

        print("\n\n" + "-" * 80 + "\n\n")

    sys.stdout = original_stdout

print("Les 9 modèles LMM ont été ajustés avec succès !")
print(f"Le rapport complet en français a été sauvegardé sous : {OUTPUT_TXT}")
