"""
EXTRACTION AUTOMATISÉE DES PARAMÈTRES ACOUSTIQUES DES CONSONNES

Description :
    Ce script parcourt un jeu de données de fichiers audio (.wav) et d'annotations
    (.TextGrid) pour extraire automatiquement les mesures acoustiques des consonnes :
      1. Calcul des statistiques de F0 globale par locuteur (pour la normalisation Z-score).
      2. Détection du point d'explosion (Release Burst) et calcul du VOT (ms).
      3. Mesure du taux de voisement (%) et extraction de la F0 moyenne.
      4. Détermination des contextes phonétiques (précédent/suivant) et de la position.

Sortie :
    Un fichier CSV structuré ("corpus_consonants_extraction.csv") prêt pour les analyses statistiques.
"""

import csv
import os
from pathlib import Path
import numpy as np
import pandas as pd
import parselmouth
from parselmouth.praat import call
import textgrid

# CONFIGURATION ET CONSTANTES

# [À MODIFIER] Chemin du dossier contenant les fichiers d'annotation (.TextGrid) et audio (.wav)
ROOT_OUTPUT = Path(r"X:\corpus\output")

# [À MODIFIER] Chemin vers le fichier Excel contenant les métadonnées des locuteurs (Genre, Région, etc.)
METADATA_PATH = Path(r"X:\corpus\metadata.xlsx")

# Cartographie et catégorisation des consonnes cibles
CONSONANT_CATEGORIES = {
    "p": "occlusive",
    "pʰ": "occlusive",
    "t": "occlusive",
    "tʰ": "occlusive",
    "k": "occlusive",
    "kʰ": "occlusive",
    "ʔ": "occlusive",
    "f": "fricative",
    "x": "fricative",
    "ɕ": "fricative",
    "ʂ": "fricative",
    "s": "fricative",
    "ʈʂ": "affriquée",
    "ʈʂʰ": "affriquée",
    "tɕ": "affriquée",
    "tɕʰ": "affriquée",
    "ts": "affriquée",
    "tsʰ": "affriquée",
    "m": "sonante",
    "n": "sonante",
    "ŋ": "sonante",
    "l": "sonante",
    "ʐ": "sonante",
}

# Cartographie des lieux d'articulation
CONSONANT_PLACES = {
    "p": "labial",
    "pʰ": "labial",
    "f": "labial",
    "m": "labial",
    "ts": "dental",
    "tsʰ": "dental",
    "t": "dental",
    "tʰ": "dental",
    "s": "dental",
    "n": "dental",
    "l": "dental",
    "tɕ": "alvéo-palatal",
    "tɕʰ": "alvéo-palatal",
    "ɕ": "alvéo-palatal",
    "ʂ": "retroflexe",
    "ʐ": "retroflexe",
    "ʈʂ": "retroflexe",
    "ʈʂʰ": "retroflexe",
    "k": "vélaire",
    "kʰ": "vélaire",
    "x": "vélaire",
    "ŋ": "vélaire",
    "ʔ": "glottal",
}

TARGET_CONSONANTS = set(CONSONANT_CATEGORIES.keys())
SILENCE_LABELS = {"sil", "spn", "SIL", ""}

# Définition des consonnes aspirées
ASPIRATED_CONSONANTS = {"pʰ", "tʰ", "kʰ", "ʈʂʰ", "tɕʰ", "tsʰ"}


# FONCTION DE DÉTECTION DU RELEASE BURST ET VOT PRÉCIS

def detect_release_burst(sound, t_start, t_end, search_window_before_end=0.08):
    """
    Localise précisément l'instant de l'explosion de relâchement (Release Burst) en secondes
    dans l'intervalle [t_start, t_end] en combinant l'énergie haute fréquence et la dérivée d'intensité.
    """
    t_search_start = max(t_start, t_end - search_window_before_end)
    t_search_end = t_end
    segment_duration = t_search_end - t_search_start

    if segment_duration < 0.015:
        return t_start

    sound_part = sound.extract_part(
        from_time=t_search_start, to_time=t_search_end, preserve_times=True
    )

    if segment_duration < 0.064:
        min_pitch = max(150, int(np.ceil(6.4 / segment_duration)))
    else:
        min_pitch = 100

    try:
        intensity = sound_part.to_intensity(
            minimum_pitch=min_pitch, time_step=0.001
        )
        times = intensity.xs()
        intensity_values = intensity.values[0, :]
    except Exception:
        return t_start

    if len(intensity_values) < 3:
        return t_start

    intensity_diff = np.diff(intensity_values)

    try:
        sound_filtered = call(
            sound_part, "Filter (pass band)", 1000, 8000, 100
        )
    except Exception:
        sound_filtered = sound_part

    high_freq_amp = np.abs(sound_filtered.values[0, :])
    sound_filtered_xs = sound_filtered.xs()

    hf_amp_resampled = np.interp(
        times[:-1], sound_filtered_xs, high_freq_amp
    )

    burst_score = intensity_diff * hf_amp_resampled
    max_idx = np.argmax(burst_score)

    return times[max_idx]


def calculate_burst_and_vot(sound, pitch, t_start, t_end):
    """
    Calcule l'instant du Release Burst ainsi que le Voice Onset Time (VOT) en millisecondes.
    """
    # Localisation de l'instant de l'explosion
    t_burst = detect_release_burst(sound, t_start, t_end)

    # Recherche du premier début de voisement (Voicing Onset) après le burst
    t_voicing_onset = None
    t = t_burst
    max_search_time = min(t_end + 0.15, sound.end_time)

    while t <= max_search_time:
        p_val = pitch.get_value_at_time(t)
        if p_val and not pd.isna(p_val) and p_val > 0:
            t_voicing_onset = t
            break
        t += 0.001  # Pas de 1 ms

    # Valeur de secours si aucun voisement n'est détecté
    if t_voicing_onset is None:
        t_voicing_onset = t_end

    # Calcul du VOT (ms)
    vot_ms = (t_voicing_onset - t_burst) * 1000

    return round(max(0.0, vot_ms), 2)


# CALCUL DE LA F0 GLOBALE PAR LOCUTEUR (POUR NORMALISATION Z-SCORE)

def calculate_global_f0_stats(metadata_df):
    """
    Extrait l'ensemble des valeurs de F0 de chaque locuteur sur la totalité de ses enregistrements
    afin de calculer sa moyenne et son écart-type globaux.
    """
    print("--- Calcul des statistiques globales de F0 par locuteur ---")
    locuteur_pitch_data = {}

    for tg_file in ROOT_OUTPUT.rglob("*.TextGrid"):
        wav_file = tg_file.with_suffix(".wav")
        if not wav_file.exists():
            wav_file = Path(
                str(tg_file).replace("output", "audios")
            ).with_suffix(".wav")
            if not wav_file.exists():
                continue

        parts = tg_file.stem.split("-")
        if len(parts) < 3:
            continue
        locuteur = parts[2]

        meta_row = metadata_df[metadata_df["ID locuteur"] == locuteur]
        sexe = (
            str(meta_row["Genre"].values[0]).strip().upper()
            if not meta_row.empty
            else "F"
        )
        # Ajustement du plafond du Pitch selon le genre
        pitch_ceiling = 250 if sexe == "M" else 500

        if locuteur not in locuteur_pitch_data:
            locuteur_pitch_data[locuteur] = []

        try:
            sound = parselmouth.Sound(str(wav_file))
            pitch = sound.to_pitch(
                time_step=0.01, pitch_floor=50, pitch_ceiling=pitch_ceiling
            )
            pitch_values = pitch.selected_array["frequency"]
            valid_pitches = pitch_values[pitch_values > 0]
            locuteur_pitch_data[locuteur].extend(valid_pitches)
        except Exception as e:
            print(
                f"[Attention] Impossible d'extraire la F0 globale pour {wav_file.name} : {e}"
            )

    locuteur_stats = {}
    for loc, values in locuteur_pitch_data.items():
        if values:
            df_temp = pd.Series(values)
            locuteur_stats[loc] = {
                "mean": df_temp.mean(),
                "std": df_temp.std(),
            }
    return locuteur_stats


# ÉTAPE 2 : EXTRACTION DES PARAMÈTRES ACOUSTIQUES DES CONSONNES

def extract_consonant_features(locuteur_stats, metadata_df):
    """
    Parcourt l'ensemble des fichiers d'annotation et extrait tous les indicateurs
    acoustiques et sociolinguistiques pour chaque consonne cible.
    """
    print(
        "\n--- Extraction complète des indicateurs acoustiques ---"
    )
    rows = []

    for tg_file in ROOT_OUTPUT.rglob("*.TextGrid"):
        wav_file = tg_file.with_suffix(".wav")
        if not wav_file.exists():
            wav_file = Path(
                str(tg_file).replace("output", "audios")
            ).with_suffix(".wav")
            if not wav_file.exists():
                continue

        fiche_origine = tg_file.stem
        parts = fiche_origine.split("-")
        if len(parts) < 3:
            continue
        locuteur = parts[2]

        meta_row = metadata_df[metadata_df["ID locuteur"] == locuteur]
        sexe_raw = (
            meta_row["Genre"].values[0] if not meta_row.empty else "Inconnu"
        )
        sexe_upper = str(sexe_raw).strip().upper()
        region = (
            meta_row["Lieu de résidence"].values[0]
            if not meta_row.empty
            else "Inconnu"
        )

        pitch_ceiling = 250 if sexe_upper == "M" else 500

        try:
            tg = textgrid.TextGrid.fromFile(str(tg_file))
            if "phones" not in tg.getNames():
                continue
            phone_tier = tg.getFirst("phones")

            sound = parselmouth.Sound(str(wav_file))
            pitch = sound.to_pitch(
                time_step=0.01, pitch_floor=50, pitch_ceiling=pitch_ceiling
            )

            num_intervals = len(phone_tier)

            for i in range(num_intervals):
                interval = phone_tier[i]
                phone_text = str(interval.mark).strip()

                if phone_text in TARGET_CONSONANTS:
                    t_start = interval.minTime
                    t_end = interval.maxTime
                    duree_ms = (t_end - t_start) * 1000
                    categorie_actuelle = CONSONANT_CATEGORIES[phone_text]
                    lieu_articulation = CONSONANT_PLACES.get(phone_text, "N/A")

                    # 1. Détermination du contexte phonétique et de la position
                    seg_avant = (
                        str(phone_tier[i - 1].mark).strip() if i > 0 else "SIL"
                    )
                    seg_apres = (
                        str(phone_tier[i + 1].mark).strip()
                        if i < num_intervals - 1
                        else "SIL"
                    )
                    if not seg_avant:
                        seg_avant = "SIL"
                    if not seg_apres:
                        seg_apres = "SIL"

                    if seg_avant in SILENCE_LABELS:
                        position = "initial"
                    elif seg_apres in SILENCE_LABELS:
                        position = "final"
                    else:
                        position = "intervocalique"

                    # 2. Classification du type d'aspiration
                    if categorie_actuelle in ["occlusive", "affriquée"]:
                        type_aspiration = (
                            "Aspiré"
                            if phone_text in ASPIRATED_CONSONANTS
                            else "Non-aspiré"
                        )
                    else:
                        type_aspiration = ""

                    # 3. Extraction du VOT (ms)
                    if categorie_actuelle in ["occlusive", "affriquée"]:
                        vot_ms = calculate_burst_and_vot(
                            sound, pitch, t_start, t_end
                        )
                    else:
                        vot_ms = "N/A"

                    # 4. Calcul du taux de voisement (%)
                    pitch_values = []
                    t = t_start
                    while t <= t_end:
                        p_val = pitch.get_value_at_time(t)
                        pitch_values.append(p_val)
                        t += 0.01

                    total_frames = len(pitch_values)
                    voiced_frames = sum(
                        1 for v in pitch_values if v > 0 and not pd.isna(v)
                    )

                    taux_voisement_pct = (
                        (voiced_frames / total_frames * 100)
                        if total_frames > 0
                        else 0.0
                    )
                    taux_voisement_str = f"{taux_voisement_pct:.2f}%"

                    local_voiced_pitches = [
                        v for v in pitch_values if v > 0 and not pd.isna(v)
                    ]
                    f0_moyenne_hz = (
                        pd.Series(local_voiced_pitches).mean()
                        if local_voiced_pitches
                        else None
                    )

                    # 5. Normalisation de la F0 (Z-Score)
                    f0_normalisee_z = None
                    if f0_moyenne_hz and locuteur in locuteur_stats:
                        u = locuteur_stats[locuteur]["mean"]
                        s = locuteur_stats[locuteur]["std"]
                        if s and s > 0:
                            f0_normalisee_z = (f0_moyenne_hz - u) / s

                    # Construction du dictionnaire d'exportation (sans t_burst ni Duree de tenue)
                    rows.append({
                        "ID_fichier": fiche_origine,
                        "Locuteur": locuteur,
                        "Genre": sexe_raw,
                        "Région": region,
                        "Consonne": phone_text,
                        "Catégorie": categorie_actuelle,
                        "Lieu d'articulation": lieu_articulation,
                        "Aspiration": type_aspiration,
                        "Durée totale (ms)": round(duree_ms, 2),
                        "VOT (ms)": vot_ms,
                        "Taux de voisement": taux_voisement_str,
                        "F0 Moyenne (Hz)": (
                            round(f0_moyenne_hz, 2) if f0_moyenne_hz else "N/A"
                        ),
                        "F0 Normalisée (Z-score)": (
                            round(f0_normalisee_z, 4)
                            if f0_normalisee_z
                            else "N/A"
                        ),
                        "Segment avant": seg_avant,
                        "Segment après": seg_apres,
                        "Position": position,
                    })

        except Exception as e:
            print(f"[Erreur] Traitement du fichier {tg_file.name} : {e}")

    # [À MODIFIER SI BESOIN] Exportation vers le fichier CSV final
    final_csv = ROOT_OUTPUT / "corpus_consonants_extraction.csv"
    df_result = pd.DataFrame(rows)
    df_result.to_csv(final_csv, index=False, encoding="utf-8-sig")
    print(f"\nExtraction terminée ! {len(rows)} consonnes extraites avec succès.")
    print(f"Le fichier final est disponible sous : {final_csv}")

# POINT D'ENTRÉE PRINCIPAL (MAIN ENTRY POINT)
if __name__ == "__main__":
    print("Démarrage du programme d'extraction acoustique...")
    if not METADATA_PATH.exists():
        print(f"[Erreur] Le fichier de métadonnées est introuvable : {METADATA_PATH}")
    elif not ROOT_OUTPUT.exists():
        print(f"[Erreur] Le dossier racine d'accès est introuvable : {ROOT_OUTPUT}")
    else:
        print(f"Chargement des métadonnées : {METADATA_PATH}")
        df_meta = pd.read_excel(METADATA_PATH)
        df_meta.columns = df_meta.columns.str.strip()
        if "ID locuteur" in df_meta.columns:
            df_meta["ID locuteur"] = (
                df_meta["ID locuteur"].astype(str).str.strip()
            )
            stats_f0 = calculate_global_f0_stats(df_meta)
            extract_consonant_features(stats_f0, df_meta)
        else:
            print("[Erreur] La colonne 'ID locuteur' est absente de l'en-tête de votre fichier Excel !")
