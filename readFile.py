import os

# Chemin vers le répertoire
def read(filename):
    # Lister tous les fichiers et dossiers dans le répertoire
    fichiers_et_dossiers = os.listdir(filename)
    fichiers = []
    # Si vous voulez seulement les fichiers, vous pouvez filtrer ainsi :
    for f in fichiers_et_dossiers:
        if os.path.isfile(os.path.join(filename, f)):
            fichiers.append(f"{filename}/{f}")
    return fichiers

