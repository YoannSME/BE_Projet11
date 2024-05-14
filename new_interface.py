import tkinter as tk
import os
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
import csv
import re

images_chargees = []
images_a_modifier = []
lst_images = []
output_csv = None
couleur = {'-1': 'white', '0': 'blue', '1': 'grey', '-1.0': 'white', '0.0': 'blue', '1.0': 'grey'}


# Fog state modification functions
def switch_to_brouillard(liste_images):
    update_image_colors(liste_images, '1')


def switch_to_not_brouillard(liste_images):
    update_image_colors(liste_images, '0')


def switch_to_indetermine(liste_images):
    update_image_colors(liste_images, '-1')


def update_image_colors(liste_images, state):
    global couleur, lst_images
    for elem in liste_images:
        elem[1] = state
        for image in lst_images:
            if elem[0] == image[1]:
                try:
                    image[0].config(highlightbackground=couleur[state], highlightthickness=4)
                except TclError:
                    pass  # The widget no longer exists


def create_message_box(liste_images):
    message_win = Tk()
    message_win.minsize(300, 100)
    message_win.maxsize(300, 100)
    message_win.title('Etat du brouillard')
    message_win.iconbitmap("montagne_icon.ico")
    Label(message_win, text="Quel est l'état du brouillard ?").pack(padx=0, pady=1)

    bouton1 = Button(message_win, text='Brouillard',
                     command=lambda: [switch_to_brouillard(liste_images), message_win.destroy()])
    bouton2 = Button(message_win, text='Pas de brouillard',
                     command=lambda: [switch_to_not_brouillard(liste_images), message_win.destroy()])
    bouton3 = Button(message_win, text='Indeterminé',
                     command=lambda: [switch_to_indetermine(liste_images), message_win.destroy()])

    bouton1.pack(padx=2, pady=0)
    bouton2.pack(padx=2, pady=1)
    bouton3.pack(padx=2, pady=2)

    message_win.mainloop()


def afficher_message(message):
    messagebox.showinfo("Information", message)


def afficher_graph():
    chemin_image = filedialog.askopenfilename()
    if chemin_image:
        graphique = Image.open(chemin_image)
        graph_redimensionne = graphique.resize((frame1.winfo_width(), frame1.winfo_height()), Image.Resampling.BICUBIC)
        graph_tk = ImageTk.PhotoImage(graph_redimensionne)
        label_graphique = Label(frame1, image=graph_tk)
        label_graphique.image = graph_tk
        label_graphique.pack()


def charger_image(chemin, largeur, hauteur):
    image = Image.open(chemin)
    image_redimensionnee = image.resize((largeur, hauteur), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image_redimensionnee)
    return photo


def mise_en_forme(image_test):
    split = image_test.split('_')
    horaire = split[4]
    horaire = horaire[:2] + ':' + horaire[2:4] + ':' + horaire[4:6]
    date = split[3]
    date = date[6:8] + '/' + date[4:6] + '/' + date[:4]
    sortie = date + ',' + horaire
    return sortie


def copier_fichier(input_csv):
    global images_a_modifier, output_csv
    modif_effectuees = [[mise_en_forme(chaque_image[0]), chaque_image[1]] for chaque_image in images_a_modifier]

    # Extract version number from filename
    match = re.search(r"_v(\d+)", input_csv)
    if match:
        version = int(match.group(1)) + 1
        new_filename = re.sub(r"_v\d+", f"_v{version}", input_csv)
    else:
        version = 1
        new_filename = re.sub(r"\.csv$", f"_v{version}.csv", input_csv)

    output_csv = new_filename

    with open(input_csv, mode='r', newline='', encoding='utf-8') as infile, \
            open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile, delimiter=';')
        writer = csv.writer(outfile, delimiter=';', quoting=csv.QUOTE_NONE, escapechar='\\')

        for row in reader:
            for i, modif in enumerate(modif_effectuees):
                nom_image, data_image = modif
                if nom_image == row[0]:
                    row[1] = str(data_image)
                    del modif_effectuees[i]
                    break
            writer.writerow(row)
    images_a_modifier = []
    return output_csv


def mise_en_forme_image(nom_image):
    nom_image = nom_image.split(",")
    nom_image[0] = nom_image[0].split("/")
    nom_image[0][0], nom_image[0][2] = nom_image[0][2], nom_image[0][0]
    finale = "".join(nom_image[0]) + nom_image[1]
    finale = finale[:8] + "_" + finale[8:]
    finale = finale.replace(":", "")
    return "Webcam_pdm_CLOUDINDEX_" + finale + "_L1a_V02_d.jpg"


def liste_date_brouillard(data):
    liste = []
    for index, row in data.iterrows():
        date = mise_en_forme_image(row.iloc[0])
        if date:
            index_fog = row.iloc[1]
            liste.append((date, index_fog, index))
    return liste


def charger_csv():
    file = filedialog.askopenfilename()
    if file:
        charger_fichier_csv(file)
    else:
        afficher_message("Aucun fichier sélectionné.")


def charger_fichier_csv(fichier_csv):
    global output_csv
    if fichier_csv is None:
        afficher_message("Le fichier CSV est manquant.")
        return
    repertoire = os.path.dirname(fichier_csv)
    data_csv = pd.read_csv(fichier_csv, sep=';', skiprows=29)
    liste_nom_images_donnees = liste_date_brouillard(data_csv)
    liste_im = [(elem[0], elem[1]) for elem in liste_nom_images_donnees]
    output_csv = fichier_csv
    afficher_images(repertoire, liste_im)


def supprimer_images():
    global images_chargees,images_a_modifier,lst_images,output_csv
    for label in frame.winfo_children():
        label.destroy()
    images_chargees.clear()
    images_a_modifier.clear()
    lst_images.clear()
    output_csv = None


def destroy():
    for label in frame.winfo_children():
        label.destroy()


def images_meme_jour(nom_image, lst_image):
    jour = nom_image[22:30]
    return [(elem, -1) for elem in lst_image if elem[22:30] == jour]


def recuperer_csv_par_image(chemin_image, dossier_image, nom_image, fichiers_images):
    date = nom_image[22:30]
    for fichier in fichiers_images:
        if fichier.endswith(".csv") and fichier[26:34] == date:
            return os.path.join(dossier_image, fichier)
    return None


def charger_images_button():
    supprimer_images()
    image_entree = filedialog.askopenfilename()
    if not image_entree:
        afficher_message("Aucune image sélectionnée.")
        return

    nom_image = os.path.basename(image_entree)
    dossier_images = os.path.dirname(image_entree)
    fichiers_images = os.listdir(dossier_images)

    fichier_csv = recuperer_csv_par_image(image_entree, dossier_images, nom_image, fichiers_images)
    if fichier_csv:
        charger_fichier_csv(fichier_csv)
    else:
        fichiers_images = images_meme_jour(nom_image, fichiers_images)
        if not fichiers_images:
            afficher_message("Il n'y a pas d'images dans le dossier spécifié.")
            return
        afficher_images(dossier_images, fichiers_images)


def on_image_click(event, param):
    global images_a_modifier
    label = event.widget
    if not hasattr(label, 'clicked'):
        label.clicked = False
        label.original_color = label.cget('highlightbackground')

    if not label.clicked:
        images_a_modifier.append([param, label.original_color])
        label.config(highlightbackground='red', highlightthickness=4)
        label.clicked = True
    else:
        images_a_modifier = [elem for elem in images_a_modifier if elem[0] != param]
        label.config(highlightbackground=label.original_color, highlightthickness=4)
        label.clicked = False


def show_loading_screen(root):
    loading_screen = Toplevel(root)
    loading_screen.title("Chargement")
    loading_screen.geometry("200x100")
    Label(loading_screen, text="Chargement en cours...").pack(expand=True)
    return loading_screen


def enregistrer_modifications():
    global output_csv,images_a_modifier,images_chargees
    if not output_csv:
        afficher_message("Aucun fichier CSV chargé.")
        return

    loading_screen = show_loading_screen(root)
    root.update_idletasks()  # Ensure the loading screen is shown

    new_csv = copier_fichier(output_csv)
    charger_fichier_csv(new_csv)

    loading_screen.destroy()  # Close the loading screen
    afficher_message(f"Fin du chargement ! nouveau fichier.csv : {os.path.basename(new_csv)}")


def afficher_item_list():
    for elem in images_a_modifier:
        print(elem)


def afficher_images(dossier_images, fichiers_images):
    destroy()
    global images_chargees
    images_chargees = []

    ligne_actuelle = Frame(frame)
    ligne_actuelle.pack(side="top", pady=5)
    compteur_images = 0
    for fichier_image in fichiers_images:
        data = fichier_image[1]
        image_etudiee = fichier_image[0]
        if image_etudiee.endswith("jpg"):
            chemin_image = os.path.join(dossier_images, image_etudiee)
            if os.path.isfile(chemin_image):
                photo = charger_image(chemin_image, 300, 250)
                images_chargees.append(photo)
                color = couleur.get(str(data), 'black')
                label_image = Label(ligne_actuelle, image=photo, borderwidth=0, highlightthickness=4,
                                    highlightbackground=color)
                label_image.image = photo
                label_image.pack(side="left", padx=2, pady=2)
                label_image.bind("<Button-1>", lambda event, arg=image_etudiee: on_image_click(event, arg))
                lst_images.append((label_image, image_etudiee))
                compteur_images += 1
                if compteur_images == 5:
                    ligne_actuelle = Frame(frame)
                    ligne_actuelle.pack(side="top", pady=5)
                    compteur_images = 0


def on_scroll(event):
    canvas.yview_scroll(-1 * (event.delta // 120), "units")


root = tk.Tk()
root.minsize(1080, 720)
root.title("MidiFog")
root.iconbitmap("../BE_Projet11/montagne_icon.ico")

frame1 = Frame(root, bd=2, relief=GROOVE)
frame1.pack(fill=BOTH, expand=True)

canvas = tk.Canvas(root)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

scrollbar2 = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
scrollbar2.pack(side="top", fill="x")

canvas.configure(yscrollcommand=scrollbar.set)
canvas.configure(xscrollcommand=scrollbar2.set)


def actualiser_canvas(event):
    canvas.configure(scrollregion=canvas.bbox("all"))


frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor="nw")
frame.bind("<Configure>", actualiser_canvas)
canvas.bind_all("<MouseWheel>", on_scroll)

menu_bar = Menu(root)
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Charger un fichier", command=charger_csv)
file_menu.add_separator()
file_menu.add_command(label="Charger une image", command=charger_images_button)
file_menu.add_separator()
file_menu.add_command(label="Supprimer les images", command=supprimer_images)
file_menu.add_separator()
file_menu.add_command(label="Afficher items", command=afficher_item_list)
file_menu.add_separator()
file_menu.add_command(label="Enregistrer", command=enregistrer_modifications)
menu_bar.add_cascade(label="Fichier", menu=file_menu)

edit_menu = Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Sélectionner", command=lambda: create_message_box(images_a_modifier))
menu_bar.add_cascade(label="Editer", menu=edit_menu)

root.config(menu=menu_bar)
root.mainloop()
