import tkinter as tk
import os
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from messagebox import create_message_box
images_chargees = []

def afficher_graph():
    # Demander à l'utilisateur de sélectionner un fichier
    chemin_image = filedialog.askopenfilename()

    # Vérifier si un fichier a été sélectionné
    if chemin_image:
        # Charger l'image
        graphique = Image.open(chemin_image)
        graph_redimensionne = graphique.resize((frame1.winfo_width(), frame1.winfo_height()), Image.Resampling.BICUBIC)
        # Convertir l'image en format Tkinter
        graph_tk = ImageTk.PhotoImage(graph_redimensionne)
        # Mettre à jour l'image affichée
        label_graphique = Label(frame1, image=graph_tk)
        label_graphique.image = graph_tk  # Garder une référence à l'image pour éviter qu'elle ne soit effacée par le
        # garbage collector
        label_graphique.pack()

def charger_image(chemin, largeur, hauteur):
    image = Image.open(chemin)
    image_redimensionnee = image.resize((largeur, hauteur), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image_redimensionnee)
    return photo

def afficher_images():

    # Supprimer les références aux images précédentes
    del images_chargees[:]

    # Chemin du dossier contenant les images
    dossier_images = filedialog.askdirectory()

    # Vérifier si le chemin du dossier est correct
    if not os.path.isdir(dossier_images):
        print("Le chemin du dossier d'images est incorrect.")
        return

    # Liste des fichiers images dans le dossier
    fichiers_images = os.listdir(dossier_images)

    # Si la liste des fichiers est vide, il n'y a pas d'images à afficher
    if not fichiers_images:
        print("Il n'y a pas d'images dans le dossier spécifié.")
        return

    # Largeur de la fenêtre
    largeur_fenetre = root.winfo_width()

    # Largeur de chaque image
    largeur_image = 200

    # Calculer le nombre d'images par ligne, en évitant la division par zéro
    images_par_ligne = max(1, largeur_fenetre // largeur_image)

    # Créer une nouvelle ligne pour afficher les images
    ligne_actuelle = Frame(frame)
    ligne_actuelle.pack(side="top", pady=5)

    # Afficher chaque image dans un label
    for i, fichier_image in enumerate(fichiers_images):
        chemin_image = os.path.join(dossier_images, fichier_image)
        photo = charger_image(chemin_image, 300, 200)  # Redimensionnez l'image à la taille souhaitée
        images_chargees.append(photo)  # Garder une référence à l'image chargée

        # Créer un nouveau label pour l'image
        label_image = Label(ligne_actuelle, image=photo)
        label_image.image = photo

        # Afficher l'image sur la ligne actuelle
        label_image.pack(side="left", padx=0, pady=0)

        # Vérifier si l'image dépasse la largeur de la fenêtre
        if (i + 1) % images_par_ligne == 0 and images_par_ligne != 0:
            # Si oui, passer à la ligne suivante
            ligne_actuelle = Frame(frame)
            ligne_actuelle.pack(side="top", pady=0)

# Fonction appelée lors du défilement de la scrollbar
def on_scroll(event):
    canvas.yview_scroll(-1*(event.delta//120), "units")

# Créer une fenêtre tkinter
root = tk.Tk()

# Personalisation
root.minsize(1080, 720)
root.title("MidFog")
root.iconbitmap("C:/Users/gabri/PycharmProjects/pythonProject/montagne_icon.ico")

# Création de la 1ere frame
frame1 = Frame(root, bd=1, relief=SUNKEN)
frame1.pack(fill=BOTH, expand=True)


# Créer un Canvas pour afficher les images avec une scrollbar
canvas = tk.Canvas(root)
canvas.pack(side="left", fill="both", expand=True)

# Ajouter une scrollbar verticale au Canvas
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

# Configurer le Canvas pour scroller avec la scrollbar
canvas.configure(yscrollcommand=scrollbar.set)

# Fonction pour actualiser la zone d'affichage lors du redimensionnement
def actualiser_canvas(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

# Créer une frame à l'intérieur du Canvas
frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor="nw")

# Lier la fonction d'actualisation du Canvas à l'événement de redimensionnement
frame.bind("<Configure>", actualiser_canvas)

# Lier la fonction de défilement de la scrollbar à la molette de la souris
canvas.bind_all("<MouseWheel>", on_scroll)

# Créer la menu bar
menu_bar = Menu(root)

# Créer le menu Fichier
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Charger un fichier", command=afficher_graph)
file_menu.add_separator()
file_menu.add_command(label="Charger une image", command=afficher_images)
menu_bar.add_cascade(label="Fichier", menu=file_menu)

# Créer le menu Editer
edit_menu = Menu(menu_bar, tearoff=0)
edit_menu.add_command(label=" Sélectionner", command=create_message_box)
menu_bar.add_cascade(label="Editer", menu=edit_menu)

# Ajout de la menu bar à la fenêtre
root.config(menu=menu_bar)

# Lancer la boucle principale
root.mainloop()