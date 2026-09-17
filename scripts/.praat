# SCRIPT PRAAT : EXAMEN ET ÉDITION EN LOT DE FICHIERS TEXTGRID (BATCH REVIEW)
# 
#   Ce script permet d'ouvrir séquentiellement des couples de fichiers audio (.wav)
#   et d'annotations (.TextGrid) situés dans des répertoires distincts à partir
#   d'une liste textuelle de noms de fichiers.
# 
# Fonctions principales :
#   - Reprise à n'importe quel point du traitement (gestion des points d'arrêt / start_from).
#   - Affichage de l'index de progression dans la fenêtre d'information de Praat.
#   - Sauvegarde automatique du TextGrid modifié dans son répertoire d'origine.


form Batch review (separate dirs)
    # [À MODIFIER] Nom/chemin du fichier texte contenant la liste des identifiants de fichiers (un par ligne, sans extension)
    sentence fileList liste_fichier.txt
    
    # [À MODIFIER] Répertoire contenant les fichiers audio d'origine (.wav) (N'oubliez pas le symbole '\' ou '/' final)
    sentence audioDir X:\corpus\audios\
    
    # [À MODIFIER] Répertoire contenant les fichiers d'annotation (.TextGrid)
    sentence textGridDir X:\corpus\output\
    
    # [À MODIFIER SI REPRISE] Index de départ pour la boucle (1 par défaut, ou indiquez le numéro de votre point d'arrêt)
    integer start_from 1
endform

# Lecture du fichier texte contenant la liste des noms de fichiers
strings = Read Strings from raw text file: fileList$
num = Get number of strings

# Boucle d'inspection et d'édition (du fichier 'start_from' jusqu'à la fin)
for i from start_from to num
    selectObject: strings
    relPath$ = Get string: i

    # [À MODIFIER SI EXTENSION DIFFÉRENTE] Reconstruction des chemins d'accès absolus
    soundPath$ = audioDir$ + relPath$ + ".wav"
    tgPath$ = textGridDir$ + relPath$ + ".TextGrid"

    # Affichage du statut de progression dans la fenêtre d'information Praat
    appendInfoLine: "Index actuel : ", i, " / ", num, " - Traitement de : ", relPath$

    # Chargement en mémoire du fichier audio Sound
    Read from file: soundPath$
    sound = selected("Sound")

    # Chargement en mémoire du fichier d'annotation TextGrid
    Read from file: tgPath$
    tg = selected("TextGrid")

    # Ouverture simultanée du Sound et du TextGrid dans l'éditeur Praat
    selectObject: sound, tg
    View & Edit

    # Interruption temporaire du script : permet à l'utilisateur de vérifier/corriger l'alignement.
    # Cliquez sur "OK" pour enregistrer et passer au suivant, ou "Stop" pour interrompre le script.
    pause Fichier actuel (Index: 'i'). Cliquez sur OK pour sauvegarder et continuer, ou Stop pour quitter.

    # Sauvegarde automatique des modifications apportées au fichier TextGrid
    selectObject: tg
    Save as text file: tgPath$

    # Nettoyage des objets en mémoire afin d'éviter la saturation de la liste des objets Praat
    removeObject: sound, tg
endfor

# Nettoyage final et clôture du traitement
selectObject: strings
Remove
appendInfoLine: "Traitement terminé avec succès pour l'ensemble de la liste !"
