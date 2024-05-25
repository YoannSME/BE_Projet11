import tkinter as tk
import os
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
import csv
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import re
from datetime import datetime, timedelta


#Variables globales pour la gestion des images
images_chargees = []
images_a_modifier = []
images_a_enregistrer = set()
lst_images = []
output_csv = None

#Dictionnaire d'association Donnée-Couleur
couleur = {'-1': 'white', '0': 'blue', '1': 'grey', '-1.0': 'white', '0.0': 'blue', '1.0': 'grey'}


# Fonctions permettant de modifier la valeur associée au brouillard
def switch_to_brouillard(liste_images):
    update_image_colors(liste_images, '1.0')

def switch_to_not_brouillard(liste_images):
    update_image_colors(liste_images, '0.0')

def switch_to_indetermine(liste_images):
    update_image_colors(liste_images, '-1.0')

#Fonction permettant de changer la couleur des images sélectionnées
def update_image_colors(liste_images, state):
    global couleur, lst_images, images_a_enregistrer
    if(len(images_a_enregistrer) == 0):
        afficher_message("Aucune image sélectionnée")
        return
    for chaque_image in liste_images:
        chaque_image[1] = state
        for image in lst_images:
            if chaque_image[0] == image[1]:
                add_to_ens((chaque_image[0], state),images_a_enregistrer)
                try:
                    image[0].config(highlightbackground=couleur[state], highlightthickness=4)
                    image[0].clicked = False
                except TclError:
                    pass  # The widget no longer exists
    images_a_modifier.clear()




def create_message_box(liste_images):
    message_win = Tk()
    message_win.minsize(300, 100)
    message_win.maxsize(300, 100)
    message_win.title('Etat du brouillard')
    message_win.iconbitmap("Icones/montagne_icon.ico")
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

#Fonction pour afficher une image PNG (ici le graphe de donnée) dans une frame
def afficher_graph(nom_image):
    global frame1
    chemin_image = os.path.abspath(os.path.join(os.path.dirname(nom_image), nom_image))
    if chemin_image:
        if hasattr(afficher_graph, 'label_graphique'):
            afficher_graph.label_graphique.destroy()
        graphique = Image.open(chemin_image)
        graph_redimensionne = graphique.resize((frame1.winfo_width()+50, frame1.winfo_height()-50), Image.Resampling.BICUBIC)
        graph_tk = ImageTk.PhotoImage(graph_redimensionne)

        afficher_graph.label_graphique = Label(frame1, image=graph_tk)
        afficher_graph.label_graphique.image = graph_tk
        afficher_graph.label_graphique.pack()

#Fonction de normalisation de l'heure
def heure(date):
    date = date.split(",")
    time = date[1].split(":")[:2]
    return ":".join(time)

#Fonction de normalisation du nom du fichier csv
def create_nom_csv(image_test):
    return "pdm_Webcam_L2a_CLOUDINDEX_" + os.path.basename(image_test)[22:30] + "_v01.csv"
def formeLigne(valeur, couleur):
    return plt.vlines(valeur, ymin=-1, ymax=1, color=couleur, linewidth=3)

#Création d'un fichier CSV de base lorsque il n'y a aucun fichier CSV présent
def create_base_csv(image_test):
    # Extraire le répertoire courant de l'image_test
    directory = os.path.dirname(image_test)

    # Créer le nom du fichier CSV
    nom_csv = create_nom_csv(image_test)
    # Chemin complet du fichier CSV dans le même répertoire que l'image_test
    full_csv_path = os.path.join(directory, nom_csv)

    horaire = mise_en_forme(os.path.basename(image_test))
    date = horaire.split(',')[0]
    entete = [
        "# TITLE: Webcam - L2A - Cloud rate calculation",
        "# FILE NAME: " + nom_csv,
        "# DATA FORMAT: Version 1.0",
        "# HEADER LINES: 30",
        "# TOTAL LINES: 318",
        "# DATA PRODUCT TYPE: L2A",
        "# SOFTWARE VERSION: 2.7",
        "# CAMERA MODEL: TRENDNET_IP313PI",
        "# STATION CODE: PDM",
        "# STATION NAME: Pic du Midi de Bigorre",
        "# STATION CATEGORY: Contributing",
        "# CONTRIBUTOR: Laboratoire d'aérologie (LAERO)",
        "# COUNTRY/TERRITORY: France",
        "# LATITUDE: 42.93701",
        "# LONGITUDE: 0.141397",
        "# ALTITUDE: 2877 m",
        "# LOCATION: TDF",
        "# CONTACT POINT: gilles.athier@aero.obs-mip.fr, francois.gheusi@aero.obs-mip.fr",
        "# PARAMETER: Cloud_Index",
        "# COVERING PERIOD: " + date + ",00:00:00 " + date + ",23:55:00",
        "# TIME INTERVAL: 5 minutes",
        "# DATA POLICY: P2OA (https://p2oa.aeris-data.fr/p2oa-data-policy)",
        "# COMMENT:",
        "#  - Times are UTC",
        "#  - Cloud_Index are without unit",
        "#    - missing_value: -1.0",
        "#    - valid_min: 0.0 indicates no cloud",
        "#    - valid_max: 1.0 indicates presence of cloud",
        "#  - Data processing is described in",
        "#DateTime;Cloud_Index"
    ]

    debut_images = horaire[:10] + ",00:00:00"
    fin_images = horaire[:10] + ",23:55:00"
    start_time = datetime.strptime(debut_images, "%d/%m/%Y,%H:%M:%S")
    end_time = datetime.strptime(fin_images, "%d/%m/%Y,%H:%M:%S")

    # Debug: Vérification si le répertoire existe et si le chemin est correct
    if not os.path.exists(directory):
        afficher_message(f"Erreur: le répertoire {directory} n'existe pas.")
        return
    if not os.access(directory, os.W_OK):
        afficher_message(f"Erreur: le répertoire {directory} n'est pas accessible en écriture.")
        return

    with open(full_csv_path, mode='w', newline='', encoding='utf-8') as outfile:
        for elem in entete:
            outfile.write(elem + "\n")
        current_time = start_time
        while current_time <= end_time:
            outfile.write(current_time.strftime("%d/%m/%Y,%H:%M:%S") + ";-1.0" + "\n")
            current_time += timedelta(minutes=5)
    return full_csv_path

#Fonction de création d'un graphique relatif aux données associées à un fichier CSV
def creerGraphe(data, output_filename,output_dir):
    tabHeures = []
    tabBrouillard = []
    tabHeuresExact = []
    nbLignes = data.shape[0]
    date = data.iloc[0, 0]
    date = date.split(",")
    date = date[0]
    plt.figure(figsize=(15, 6))
    plt.xlabel(date)
    for i in range(nbLignes):
        h = datetime.strptime(heure(data.iloc[i, 0]), '%H:%M')
        hstring = heure(data.iloc[i, 0])
        minutes = h.minute
        if int(minutes) == 0:
            tabHeuresExact.append(hstring)
        tabHeures.append(hstring)

        indexFog = data.iloc[i, 1]
        tabBrouillard.append(indexFog)

    plt.plot(tabHeures, tabBrouillard, marker='o', color='black', linestyle='None')
    for i, valeur in enumerate(tabBrouillard):
        val_courante = tabHeures[i]
        if valeur == 1:
            formeLigne(val_courante, 'grey')
        elif valeur == 0:
            formeLigne(val_courante, 'blue')
        elif valeur == -1:
            formeLigne(val_courante, 'white')

    plt.title('Cloud index - Pic du Midi')
    legende_elements = [
        Line2D([0], [0], color='gray', linewidth=3, label='cloud'),
        Line2D([0], [0], color='blue', linewidth=3, label='no cloud'),
        Line2D([0], [0], color='white', linewidth=3, label='no data')
    ]
    plt.legend(handles=legende_elements, loc='center left', bbox_to_anchor=(1, 0.5))
    plt.yticks([])
    plt.xticks(tabHeuresExact)
    plt.ylim(-1, 1)
    plt.grid(False)
    output_path = os.path.join(os.path.abspath(output_dir),os.path.basename(output_filename)) #CREER FICHIER CSV VIDE AVEC ENTETE SI PAS DE CSV ASSOCIEES AU XIMAGES

    plt.savefig(output_path, format='jpg')
    plt.close()
    return afficher_graph(output_path)


#Fonction de normalisation pour créer un Panel image
def charger_image(chemin, largeur, hauteur):
    image = Image.open(chemin)
    image_redimensionnee = image.resize((largeur, hauteur), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(image_redimensionnee)
    return photo


#Fonction de mise en forme pour récupérer les noms des fichiers jpg et les relier au csv
def mise_en_forme(image_test):
    split = image_test.split('_')
    horaire = split[4]
    horaire = horaire[:2] + ':' + horaire[2:4] + ':' + horaire[4:6]
    date = split[3]
    date = date[6:8] + '/' + date[4:6] + '/' + date[:4]
    sortie = date + ',' + horaire
    return sortie


#Fonction pour créer un fichier.csv suite aux modifications de certaines données
def copier_fichier(input_csv):
    global images_a_modifier, output_csv,images_a_enregistrer
    modif_effectuees = [[mise_en_forme(chaque_image[0]), chaque_image[1]] for chaque_image in images_a_enregistrer]

    # Expression réguliere pour récupérer version du nom du fichier csv
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
            if "Version" in row[0]:
                # Expression réguliere pour récupérer version du csv dans le csv
                version_match = re.search(r"Version (\d+)", row[0])
                if version_match:
                    current_version = int(version_match.group(1))
                    new_version_str = f"Version {current_version + 1}"
                    row[0] = re.sub(r"Version \d+", new_version_str, row[0])
                    writer.writerow(row)
                    continue
            for i, modif in enumerate(modif_effectuees):
                nom_image, data_image = modif
                if nom_image == row[0]:
                    row[1] = str(data_image)
                    del modif_effectuees[i]
                    break
            writer.writerow(row)
    images_a_modifier = []
    images_a_enregistrer.clear()
    return output_csv

#Fonction de normalisation du nom de l'image.jpg
def mise_en_forme_image(nom_image):
    nom_image = nom_image.split(",")
    nom_image[0] = nom_image[0].split("/")
    nom_image[0][0], nom_image[0][2] = nom_image[0][2], nom_image[0][0]
    finale = "".join(nom_image[0]) + nom_image[1]
    finale = finale[:8] + "_" + finale[8:]
    finale = finale.replace(":", "")
    return "Webcam_pdm_CLOUDINDEX_" + finale + "_L1a_v02_d.jpg"

#Fonction pour récupérer les données présentes dans le CSV du type ("nom image",data)
def liste_date_brouillard(data):
    liste = []
    for index, row in data.iterrows():
        date = mise_en_forme_image(row.iloc[0])
        if date:
            index_fog = row.iloc[1]
            liste.append((date, index_fog, index))
    return liste

#Fonction pour permettre à l'utilisateur de sélectionner un fichier.csv
def charger_csv():
    file = filedialog.askopenfilename()
    if file and file.endswith('.csv'):
        charger_fichier_csv(file)
    else:
        afficher_message("Aucun fichier sélectionné.")


#Fonction pour afficher les images en rapport avec le fichier csv chargé
def charger_fichier_csv(fichier_csv):
    global output_csv,lst_images
    supprimer_images()
    lst_images.clear()
    if fichier_csv is None:
        afficher_message("Le fichier CSV est manquant.")
        return

    repertoire = os.path.dirname(fichier_csv)
    data_csv = pd.read_csv(fichier_csv, sep=';', skiprows=29)
    nom_image = fichier_csv.replace(".csv", ".png")
    creerGraphe(data_csv, nom_image,"graphiques")
    check_all_selected()
    liste_nom_images_donnees = liste_date_brouillard(data_csv)
    liste_im = [(elem[0], elem[1]) for elem in liste_nom_images_donnees]
    output_csv = fichier_csv
    loading_screen = show_loading_screen(root)
    root.update_idletasks()  # Ensure the loading screen is shown

    afficher_images(repertoire, liste_im)

    loading_screen.destroy()


#Fonction pour supprimer les données de la fenêtre
def supprimer_images():
    global images_chargees,images_a_modifier,lst_images,output_csv
    for label in frame.winfo_children():
        label.destroy()
    images_chargees.clear()
    images_a_modifier.clear()
    images_a_enregistrer.clear()
    if hasattr(afficher_graph, 'label_graphique'):
        afficher_graph.label_graphique.destroy()
        del afficher_graph.label_graphique
    output_csv = None


def destroy():
    for label in frame.winfo_children():
        label.destroy()

#Fonction pour récupérer les images du même jour
def images_meme_jour(nom_image, lst_image):
    jour = nom_image[22:30]
    return [(elem, -1) for elem in lst_image if elem[22:30] == jour]

#Fonction permettant de récupérer un fichier.csv si il est présent, à partir d'une image.png en entrée
def recuperer_csv_par_image(dossier_image, nom_image, fichiers_images):
    date = nom_image[22:30]
    liste_fichiers_csv = []
    for fichier in fichiers_images:
        if fichier.endswith(".csv") and fichier[26:34] == date:
            liste_fichiers_csv.append(fichier)

    if len(liste_fichiers_csv) == 0:
        return None
    return os.path.join(dossier_image, liste_fichiers_csv[-1])


#Event associé au bouton "Charger une image"
def charger_images_button():
    supprimer_images()
    image_entree = filedialog.askopenfilename()
    if not image_entree or not image_entree.endswith('jpg'):
        afficher_message("Aucune image sélectionnée.")
        return

    nom_image = os.path.basename(image_entree)
    dossier_images = os.path.dirname(image_entree)
    fichiers_images = os.listdir(dossier_images)

    fichier_csv = recuperer_csv_par_image(dossier_images, nom_image, fichiers_images)
    if fichier_csv:
        charger_fichier_csv(fichier_csv)
    else:
        fichiers_images = images_meme_jour(nom_image, fichiers_images)
        if not fichiers_images:
            afficher_message("Il n'y a pas d'images dans le dossier spécifié.")
        fichier_csv = create_base_csv(image_entree)
        charger_fichier_csv(fichier_csv)

#Création de fonctions de manipulation d'ensemble pour garder une trace des modifications effectuées
def add_to_ens(val,ens):
    chemin_image = val[0]

    for elem in ens:
        if chemin_image == elem[0]:
            ens.remove(elem)
            ens.add(val)
            return ens
    return ens.add(val)

def remove_from_ens(val,ens):
    chemin_image = val[0]
    for elem in ens:
        if chemin_image == elem[0]:
            ens.remove(elem)
            return ens
    return ens


#Fonction permettant un évènement lorsqu'une image est cliquée
def on_image_click(event, param):
    global images_a_modifier,images_a_enregistrer
    label = event.widget
    if not hasattr(label, 'clicked'):
        label.clicked = False
        label.original_color = label.cget('highlightbackground')

    if not label.clicked:
        images_a_modifier.append([param, label.original_color])
        add_to_ens((param,label.original_color),images_a_enregistrer)
        label.config(highlightbackground='red', highlightthickness=4)
        label.clicked = True
    else:
        images_a_modifier = [elem for elem in images_a_modifier if elem[0] != param]
        remove_from_ens((param,0),images_a_enregistrer)
        label.config(highlightbackground=label.original_color, highlightthickness=4)
        label.clicked = False
    check_all_selected()


def show_loading_screen(root):
    loading_screen = Toplevel(root)
    loading_screen.title("Chargement")

    # Dimensions de l'écran de chargement
    width = 300
    height = 150

    # Dimensions de la fenêtre principale
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (width // 2)-100
    y = (root.winfo_screenheight() // 2) - (height // 2)-100

    # Centrer l'écran de chargement
    loading_screen.geometry(f"{width}x{height}+{x}+{y}")

    # Créer un label centré
    label = Label(loading_screen, text="Chargement en cours...", font=("Arial", 8))
    label.pack(expand=True)

    return loading_screen

#Event relié au bouton "Enregistrer"
def enregistrer_modifications():
    global output_csv,images_a_modifier,images_chargees

    if not output_csv:
        afficher_message("Aucun fichier CSV chargé.")
        return
    if len(images_a_enregistrer)==0:
        afficher_message("Aucune image sélectionnée.")
        return
    for elem in images_a_enregistrer:
        if(elem[1] not in couleur.keys()):
            afficher_message("Aucune modification effectuée sur la photo "+elem[0])
            return

    loading_screen = show_loading_screen(root)
    root.update_idletasks()  # Ensure the loading screen is shown

    new_csv = copier_fichier(output_csv)
    charger_fichier_csv(new_csv)

    loading_screen.destroy()  # Close the loading screen
    afficher_message(f"Fin du chargement ! nouveau fichier.csv : {os.path.basename(new_csv)}")



#Fonction permettant d'afficher des images suivant une taille définie, dans une frame.
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
            elif not os.path.isfile(chemin_image) and data != -1.0:
                photo = charger_image("Icones/croix.jpg",300,250)
            else:
                continue
            images_chargees.append(photo)
            color = couleur.get(str(data), 'black')
            label_image = Label(ligne_actuelle, image=photo, borderwidth=0, highlightthickness=4,
                                highlightbackground=color)
            label_image.image = photo
            label_image.pack(side="left", padx=2, pady=2)
            label_image.bind("<Button-1>", lambda event, arg=image_etudiee: on_image_click(event, arg))
            label_image.clicked = False
            label_image.original_color = color
            lst_images.append((label_image, image_etudiee))
            compteur_images += 1
            if compteur_images == 5:
                ligne_actuelle = Frame(frame)
                ligne_actuelle.pack(side="top", pady=5)
                compteur_images = 0
def check_all_selected():
    if len(images_a_enregistrer)==0 or len(images_a_modifier)== 0:
        selection_label.config(text="Aucune image sélectionnée", fg="red")
    elif len(images_a_enregistrer) == len(lst_images):
        selection_label.config(text="Toutes les images sont sélectionnées", fg="green")
    else:
        selection_label.config(text=f"{len(images_a_enregistrer)} images sélectionnées", fg="orange")

#Event associé au bouton "Tout sélectionner"
def tout_selectionner():
    global images_a_modifier,images_a_enregistrer
    images_a_modifier.clear()
    images_a_enregistrer.clear()
    for label,param in lst_images:
        label.clicked = True
        label.config(highlightbackground='red', highlightthickness=4)
        images_a_modifier.append([param,label.original_color])
        add_to_ens((param, label.original_color),images_a_enregistrer)
        check_all_selected()
#Event associé au bouton "Tout désélectionner"
def tout_de_selectionner():
    global images_a_modifier,images_a_enregistrer
    images_a_modifier.clear()
    images_a_enregistrer.clear()
    for label,param in lst_images:
        label.clicked = False
        label.config(highlightbackground=label.original_color, highlightthickness=4)
        check_all_selected()

def on_scroll(event):
    canvas.yview_scroll(-1 * (event.delta // 120), "units")

def actualiser_canvas(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)



#############-MAIN-###############
root = tk.Tk()
root.minsize(1080, 720)
root.title("MidiFog")
root.iconbitmap("Icones/montagne_icon.ico")

selection_label = tk.Label(root, text="Aucune image sélectionnée", fg="black")
selection_label.pack(anchor="nw", padx=10, pady=5)

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
file_menu.add_command(label="Tout sélectionner",command=tout_selectionner)
file_menu.add_separator()
file_menu.add_command(label="Tout désélectionner",command=tout_de_selectionner)
file_menu.add_separator()
file_menu.add_command(label="Supprimer les images", command=supprimer_images)
file_menu.add_separator()
file_menu.add_command(label="Enregistrer", command=enregistrer_modifications)


menu_bar.add_cascade(label="Fichier", menu=file_menu)

edit_menu = Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Modifier brouillard", command=lambda: create_message_box(images_a_modifier))
menu_bar.add_cascade(label="Editer", menu=edit_menu)

root.config(menu=menu_bar)

# Création du menu contextuel
context_menu = Menu(root, tearoff=0)

# Créer un sous-menu pour "Fichier"
fichier_submenu = Menu(context_menu, tearoff=0)
fichier_submenu.add_command(label="Charger un fichier", command=charger_csv)
fichier_submenu.add_separator()
fichier_submenu.add_command(label="Charger une image", command=charger_images_button)
fichier_submenu.add_separator()
fichier_submenu.add_command(label="Tout sélectionner",command=tout_selectionner)
fichier_submenu.add_separator()
fichier_submenu.add_command(label="Tout désélectionner",command=tout_de_selectionner)
fichier_submenu.add_separator()
fichier_submenu.add_command(label="Supprimer les images", command=supprimer_images)
fichier_submenu.add_separator()
fichier_submenu.add_command(label="Enregistrer", command=enregistrer_modifications)
context_menu.add_cascade(label="Fichier", menu=fichier_submenu)


# Créer un sous-menu pour "Éditer"
editer_submenu = Menu(context_menu, tearoff=0)
editer_submenu.add_command(label="Modifier brouillard", command=lambda: create_message_box(images_a_modifier))
context_menu.add_cascade(label="Éditer", menu=editer_submenu)

# Liaison du clic droit pour afficher le menu contextuel sur le canvas et le frame
canvas.bind("<Button-3>", show_context_menu)
frame.bind("<Button-3>", show_context_menu)
root.bind("<Button-3>", show_context_menu)

root.mainloop()
