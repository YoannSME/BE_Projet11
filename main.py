import pandas as pd
import os
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox

def miseEnForme(nom_image): #Adapte le nom de l'image au fichier
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

def getAllImage(nom_image,lst_images):#A partir d'une image de base, récupère toutes les images du même jour qui sont présente dans le répertoire
    jourAssocie = nom_image[22:30]
    print("jour associe = "+jourAssocie)
    
    imagesAssociees = []
    for elem in lst_images:

        if(elem[0][22:30] == jourAssocie):
            imagesAssociees.append(elem)
    return imagesAssociees




def afficherImages(chemins_images, start_index):
    global image_labels
    image_labels = [label for label in image_labels if label.winfo_exists()]
    for label in image_labels:
        label.grid_forget()
        label.destroy()
    image_labels.clear()

    end_index = min(start_index + 6, len(chemins_images))
    for i in range(start_index, end_index):
        try:
            image_pil = Image.open(chemins_images[i])
            image_pil = image_pil.resize((200, 200))
            image_tk = ImageTk.PhotoImage(image_pil)

            label_image = tk.Label(root, image=image_tk)
            label_image.image = image_tk
            label_image.grid(row=(i - start_index) // 3, column=(i - start_index) % 3, padx=5, pady=5)
            image_labels.append(label_image)
        except IOError:
            messagebox.showerror("Error", f"Failed to load image: {chemins_images[i]}")

def navigate_images(direction):
    global current_index
    if direction == "suivant" and current_index + 6 <len(chemins_images):
        current_index += 6
    elif direction == "précédent" and current_index - 6 >= 0:
        current_index -= 6
    afficherImages(chemins_images, current_index)

def miseEnFormeRepertoire(listeDonnees):
    chemin = 'images/'
    chemins_images = [chemin + elem[0] for elem in listeDonnees if os.path.isfile(chemin + elem[0])]
    return chemins_images


def setup_navigation_buttons():
    next_button = tk.Button(root, text="Suivant", command=lambda: navigate_images("suivant"))
    next_button.grid(row=3, column=2, sticky=tk.E, padx=20, pady=20)
    prev_button = tk.Button(root, text="Précédent", command=lambda: navigate_images("précédent"))
    prev_button.grid(row=3, column=0, sticky=tk.W, padx=20, pady=20)

data = pd.read_csv("pdm_Webcam_L2a_CLOUDINDEX_20220218_v01.csv", sep=';', skiprows=29)
lst = listeDateBrouillard(data)

root = tk.Tk()
largeur = root.winfo_screenwidth()
hauteur = root.winfo_screenheight()
root.geometry(f"{largeur}x{hauteur}")

chemins_images = miseEnFormeRepertoire(lst)
current_index = 0
image_labels = []

test = lst[0][0]
listIm = getAllImage(test,lst) #A partir d'une image de base, récupère toutes les images du même jour dans un répertoire
afficherImages(miseEnFormeRepertoire(listIm),current_index)

#afficherImages(chemins_images, current_index)
setup_navigation_buttons()



root.mainloop()
