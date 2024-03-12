import os
from tkinter import Tk, Label, Frame
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
from tkinter import ttk

def charger_et_redimensionner_image(chemin_image, nouvelle_taille):
    image = Image.open(chemin_image)
    image_redimensionnee = image.resize(nouvelle_taille)  # ANTIALIAS pour une meilleure qualité
    return ImageTk.PhotoImage(image_redimensionnee)

def on_drop(event):
    directory_path = event.data
    if os.path.isdir(directory_path):
        load_and_display_images_from_directory(directory_path)

def load_and_display_images_from_directory(directory_path):
    global photos  # Rend la liste des photos accessible globalement
    photos.clear()  # Efface la liste des photos précédentes
    chemins_images = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    for chemin_image in chemins_images:
        photo = charger_et_redimensionner_image(chemin_image, taille_image)
        photos.append(photo)
    update_combobox_options()
    update_display(0)  # Affiche les premières 5 images

def update_combobox_options():
    options = [f"{i//5 + 1}-{min((i//5 + 1) * 5, len(photos))}" for i in range(0, len(photos), 5)]
    combobox['values'] = options
    if options:
        combobox.current(0)
        combobox.event_generate("<<ComboboxSelected>>")

def update_display(start_index):
    for widget in frame_images.winfo_children():
        widget.destroy()
    for index in range(start_index, min(start_index + 5, len(photos))):
        label = Label(frame_images, image=photos[index])
        label.pack(side="left", padx=5, pady=5)

def on_combobox_change(event):
    selected_index = int(combobox.get().split('-')[0]) - 1
    update_display(selected_index * 5)

app = TkinterDnD.Tk()
app.title("Glisser et déposer pour afficher des images")
app.geometry("520x150")  # Dimension pour afficher 5 images

taille_image = (100, 100)
photos = []

frame_images = Frame(app)
frame_images.pack()

# Ajout du message invitant à faire glisser des fichiers
invite_label = Label(app, text="Veuillez faire glisser un fichier ou un répertoire ici")
invite_label.pack(pady=10)

combobox = ttk.Combobox(app, state="readonly")
combobox.pack(pady=10)
combobox.bind("<<ComboboxSelected>>", on_combobox_change)

app.drop_target_register(DND_FILES)
app.dnd_bind('<<Drop>>', on_drop)

app.mainloop()
