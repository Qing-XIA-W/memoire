"""
AJUSTEMENT ET EXPORTATION DES MODÈLES MIXTES SOCIOLINGUISTIQUES (LMM)
==============================================================================
Description :
    Ce script ajuste les modèles linéaires mixtes (LMM 1 à 3) pour analyser 
    l'effet des facteurs sociolinguistiques (Genre et Région d'origine) sur les 
    indicateurs acoustiques (Log_Durée, Log_VOT, Logit_Voisement).

    Modales de référence (Baseline / Intercept) :
      - Genre  : 'F' (Femme)
      - Région : 'Hong Kong'
    Effet aléatoire :
      - (1 | Locuteur)
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# Ignorer les avertissements de convergence secondaires
warnings.filterwarnings("ignore")

#  CHEMINS D'ACCÈS ET CONFIGURATION

# [À MODIFIER] Chemin d'accès au fichier CSV du sous-corpus
CSV_PATH = r"X:\corpus\Souscorpus.csv"

# [À MODIFIER] Chemin du fichier texte de sortie pour l'exportation des résultats
OUTPUT_TXT = r"X:\corpus\output\Resume_Modeles_socio_LMM.txt"

os.makedirs(os.path.dirname(OUTPUT_TXT), exist_ok=True)
df = pd.read_csv(CSV_PATH)

# NORMALISATION ET PRÉTRAITEMENT DES DONNÉES

# Harmonisation des nommages de colonnes
rename_dict = {
    "Durée totale (ms)": "Duree_ms",
    "Taux de voisement": "Taux_voisement_raw",
    "VOT (ms)": "VOT_ms",
    "Genre": "Genre",
    "Région": "Region",
    "Lieu de résidence": "Region",
}
df = df.rename(columns=rename_dict)

# Nettoyage des espaces superflus pour les variables catégorielles
for col in ["Genre", "Region", "Locuteur"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

# Nettoyage et harmonisation de la variable Région (Fusion Taipei -> Taiwan)
df["Region"] = df["Region"].replace(
    {
        "Taipei": "Taiwan",
        "Taïpei": "Taiwan",
        "Taipei City": "Taiwan",
        "-": np.nan,
        "N/A": np.nan,
        "nan": np.nan,
    }
)

# Nettoyage de la variable Genre
df["Genre"] = df["Genre"].replace(
    {"m": "M", "f": "F", "homme": "M", "femme": "F", "-": np.nan, "nan": np.nan}
)

# Conversion numérique et transformations logarithmiques/logit
df["Duree_ms"] = pd.to_numeric(df["Duree_ms"], errors="coerce")
df["VOT_ms"] = pd.to_numeric(df["VOT_ms"], errors="coerce")

df["Log_Duree"] = np.log(df["Duree_ms"])
df["Log_VOT"] = np.log(df["VOT_ms"] + 1.0)

# Transformation Logit Squeezed pour le Taux de voisement
df["Voisement_num"] = pd.to_numeric(
    df["Taux_voisement_raw"].astype(str).str.rstrip("%"), errors="coerce"
)
p_raw = (df["Voisement_num"] / 100.0).clip(lower=0.0, upper=1.0)
N = len(df)
p_squeezed = (p_raw * (N - 1) + 0.5) / N
df["Logit_Voisement"] = np.log(p_squeezed / (1.0 - p_squeezed))

# FIXATION DES NIVEAUX DE RÉFÉRENCE (HONG KONG & FEMME)

# Définition rigoureuse des catégories pandas avec la référence en première position
regions_unique = [r for r in df["Region"].dropna().unique() if r != "Hong Kong"]
genres_unique = [g for g in df["Genre"].dropna().unique() if g != "F"]

df["Region"] = pd.Categorical(
    df["Region"], categories=["Hong Kong"] + sorted(regions_unique), ordered=False
)
df["Genre"] = pd.Categorical(
    df["Genre"], categories=["F"] + sorted(genres_unique), ordered=False
)

# Définition des Modèles 1, 2 et 3
formulas = {
    "Modèle 1 (Log_Durée ~ Genre + Region)": "Log_Duree ~ Genre + Region",
    "Modèle 2 (Log_VOT ~ Genre + Region)": "Log_VOT ~ Genre + Region",
    "Modèle 3 (Logit_Voisement ~ Genre + Region)": "Logit_Voisement ~ Genre + Region",
}

# AJUSTEMENT LMM ET EXPORTATION DU RAPPORT EN FRANÇAIS
print("Ajustement des Modèles 1, 2 et 3 en LMM (effets aléatoires par locuteur)...")
print(f"Les résultats seront exportés vers le fichier texte :\n{OUTPUT_TXT}\n")

with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
    original_stdout = sys.stdout
    sys.stdout = f

    print("=" * 80)
    print("   RÉSUMÉ DES RÉSULTATS LMM (EFFETS MIXTES) : MODÈLES 1 À 3")
    print("=" * 80)
    print(f"Effectif total du sous-corpus : {len(df)}")
    print(f"Locuteurs uniques (Locuteur) : {df['Locuteur'].nunique()}")
    print("-" * 80)
    print(" Modalités de référence (Baseline / Intercept) :")
    print("   - Genre  : 'F' (Femme)")
    print("   - Région : 'Hong Kong'")
    print("   -> L'Intercept représente la valeur estimée pour une locutrice Féminine de Hong Kong.")
    print("   -> Structure : Modèle linéaire mixte avec intercept aléatoire (1 | Locuteur).")
    print("=" * 80 + "\n\n")

    for name, formula in formulas.items():
        print("=" * 80)
        print(f" Ajustement du modèle mixte : {name}")
        print(f" Formule syntaxique : {formula} + (1 | Locuteur)")
        print("=" * 80)

        # Extraction propre des colonnes utilisées dans la formule
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
                f" Effectif valide (après suppression NA VOT/Genre/Region) : {len(df_clean)} / {len(df)}"
            )
        else:
            print(
                f" Effectif valide (après suppression NA Genre/Region) : {len(df_clean)} / {len(df)}"
            )

        try:
            # Modèle LMM avec intercept aléatoire par locuteur
            model = smf.mixedlm(
                formula, data=df_clean, groups=df_clean["Locuteur"]
            )
            
            # Utilisation de l'algorithme Powell pour une convergence optimale
            result = model.fit(reml=True, method="powell", maxiter=1000)
            
            print(result.summary())

        except Exception as e:
            print(f"[ERREUR] Échec de l'ajustement LMM pour {name} : {e}")

        print("\n\n" + "-" * 80 + "\n\n")

    sys.stdout = original_stdout

print(f"Ajustement des modèles 1, 2 et 3 terminé avec succès !")
print(f"Le rapport en français a été sauvegarde sous : {OUTPUT_TXT}")
