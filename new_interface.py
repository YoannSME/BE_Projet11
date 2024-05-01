import tkinter as tk
import os
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
from messagebox import create_message_box
import pandas as pd
images_chargees = []
couleur = {'-1' : 'white','0':'blue','1' : 'grey','-1.0' : 'white','0.0':'blue','1.0' : 'grey'}
images_a_modifier = []
lst_images = []
############CREER POP-UP POUR MAUVAISES MANIP fonction("message à afficher"#############)
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

def miseEnForme(nom_image):  # Adapte le nom de l'image au fichier
    nom_image = nom_image.split(",")
    nom_image[0] = nom_image[0].split("/")
    nom_image[0][0], nom_image[0][2] = nom_image[0][2], nom_image[0][0]
    finale = "".join(nom_image[0]) + nom_image[1]
    finale = finale[:8] + "_" + finale[8:]
    finale = finale.replace(":", "")
    return "Webcam_pdm_CLOUDINDEX_" + finale + "_L1a_V02_d.jpg"
def listeDateBrouillard(data):
    liste = []
    for index, row in data.iterrows():
        date = miseEnForme(row.iloc[0])
        if date:
            indexFog = row.iloc[1]
            liste.append((date, indexFog))
    return liste
def charger_fichierCSV():

    repertoire = filedialog.askdirectory()
    if(repertoire):
        fichierCSV = filedialog.askopenfilename()
        if fichierCSV.endswith(".csv"):
            dataCSV = pd.read_csv(fichierCSV,sep = ';',skiprows = 29)
            liste_nom_images_donnees = listeDateBrouillard(dataCSV)
            liste_nom_images =[]
            liste_data_images =[]

            for elem in liste_nom_images_donnees:
                liste_nom_images.append(elem[0])
                liste_data_images.append(elem[1])
            afficher_images(repertoire, liste_nom_images,liste_data_images)



def supprimer_images():
    for label in frame.winfo_children():
        label.destroy()
    del(images_chargees[:])

def destroy():
    for label in frame.winfo_children():
        label.destroy()

def charger_images_Button():
    destroy()
    dossier_images = filedialog.askdirectory()
    fichiers_images = os.listdir(dossier_images)
    if not os.path.isdir(dossier_images):
        print("Le chemin du dossier d'images est incorrect.")
        return
    if not fichiers_images:
        print("Il n'y a pas d'images dans le dossier spécifié.")
        return
    afficher_images(dossier_images,fichiers_images,[])


def on_image_click(event, param):
    label = event.widget
    # image non cliquée
    if not hasattr(label, 'clicked'):
        label.clicked = False
        label.original_color = label.cget('highlightbackground')
    if not label.clicked:
        images_a_modifier.append([param,label.original_color])
        print(param, "added")
        # Change the border color to indicate selection
        label.config(highlightbackground='red', highlightthickness=4)
        label.clicked = True
    else: #image cliquée

        try:
            for elem in images_a_modifier:
                if(elem[0] == param):
                    images_a_modifier.remove(elem)
            print(param, "removed")
        except ValueError:
            print("Error: Item not found in the list.")

        # Reset the border color to the original
        label.config(highlightbackground=label.original_color, highlightthickness=4)
        label.clicked = False

def enregisterModifications():
    for chemin_image in images_a_modifier:
        for image in lst_images:
            if(chemin_image[0] == image[1]):
                image[0].config(highlightbackground=couleur[chemin_image[1]], highlightthickness=4)
    images_a_modifier.clear()


def afficherItemList():
    for elem in images_a_modifier:
        print(elem)

def afficher_images(dossier_images, fichiers_images,data_image):
    destroy()

    # Supprimer les références aux images précédentes
    images_chargees = []


    # Créer une nouvelle ligne pour afficher les images
    ligne_actuelle = Frame(frame)
    ligne_actuelle.pack(side="top", pady=5)
    compteur_images = 0  # Compteur pour les images par ligne
    cpt = 0
    # Afficher chaque image dans un label
    for fichier_image in fichiers_images:
        if fichier_image.endswith(("jpg")):
            chemin_image = os.path.join(dossier_images, fichier_image)
            if os.path.isfile(chemin_image):
                cpt+=1
                photo = charger_image(chemin_image, 300, 250)  # Redimensionner l'image
                images_chargees.append(photo)  # Garder une référence à l'image chargée

                # Créer un nouveau label pour l'image
                if(data_image==[]):
                    color = 'black'
                else:
                    print(str(data_image[cpt]))
                    color = couleur[str(data_image[cpt])]
                    print(color)
                label_image = Label(ligne_actuelle, image=photo,
                                    borderwidth=0, highlightthickness=4,
                                    highlightbackground=color)
                label_image.image = photo  # Assurer que l'image reste en mémoire
                label_image.pack(side="left", padx=2, pady=2)
                label_image.bind("<Button-1>", lambda event, arg=fichier_image: on_image_click(event, arg))
                lst_images.append((label_image,fichier_image))

                compteur_images += 1  # Incrémenter le compteur d'images

                # Vérifier si la ligne a atteint 5 images
                if compteur_images == 5:
                    ligne_actuelle = Frame(frame)
                    ligne_actuelle.pack(side="top", pady=5)
                    compteur_images = 0







# Fonction appelée lors du défilement de la scrollbar
def on_scroll(event):
    canvas.yview_scroll(-1*(event.delta//120), "units")

# Créer une fenêtre tkinter
root = tk.Tk()

# Personalisation
root.minsize(1080, 720)
root.title("MidiFog")
root.iconbitmap("../BE_Projet11/montagne_icon.ico")

# Création de la 1ere frame
frame1 = Frame(root, bd=2, relief=GROOVE)
frame1.pack(fill=BOTH, expand=True)


# Créer un Canvas pour afficher les images avec une scrollbar
canvas = tk.Canvas(root)
canvas.pack(side="left", fill="both", expand=True)


# Ajouter une scrollbar verticale au Canvas
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

scrollbar2 = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
scrollbar2.pack(side="top", fill="x")

# Configurer le Canvas pour scroller avec la scrollbar
canvas.configure(yscrollcommand=scrollbar.set)
canvas.configure(xscrollcommand=scrollbar2.set)

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
file_menu.add_command(label="Charger un fichier", command=charger_fichierCSV)
file_menu.add_separator()
file_menu.add_command(label="Charger une image", command=charger_images_Button)
file_menu.add_separator()
file_menu.add_command(label="Supprimer les images",command=supprimer_images)
file_menu.add_separator()
file_menu.add_command(label="Afficher items", command=afficherItemList)
file_menu.add_separator()
file_menu.add_command(label="Enregistrer", command=enregisterModifications)
menu_bar.add_cascade(label="Fichier", menu=file_menu)

# Créer le menu Editer
edit_menu = Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Sélectionner", command=lambda: create_message_box(images_a_modifier))
menu_bar.add_cascade(label="Editer", menu=edit_menu)

# Ajout de la menu bar à la fenêtre
root.config(menu=menu_bar)

# Lancer la boucle principale
root.mainloop()