from tkinter import *

# Fonctions qui permettent de modifier l'état de brouillard d'une image
def switch_to_brouillard(liste_images):
    for elem in liste_images:
        elem[1]= '1'


def switch_to_not_brouillard(liste_images):
    for elem in liste_images:
        elem[1] = '0'


def switch_to_indetermine(liste_images):
    for elem in liste_images:
        elem[1] = '-1'


def create_message_box(liste_images):
    # Création de la fenêtre de message
    message_win = Tk()
    message_win.minsize(300, 100)
    message_win.maxsize(300, 100)
    message_win.title('Etat du brouillard')
    message_win.iconbitmap("montagne_icon.ico")
    Label(message_win, text="Quel est l'état du brouillard ?").pack(padx=0, pady=1)

    # Création des boutons
    bouton1 = Button(message_win, text='Brouillard', command=lambda: switch_to_brouillard(liste_images))
    bouton2 = Button(message_win, text='Pas de brouillard', command=lambda: switch_to_not_brouillard(liste_images))
    bouton3 = Button(message_win, text='Indeterminé', command=lambda: switch_to_indetermine(liste_images))

    label1 = Label(text="")
    label1.pack(padx=1, pady=1)

    # Position des boutons dans la fenêtre
    bouton1.pack(padx=2, pady=0)
    bouton2.pack(padx=2, pady=1)
    bouton3.pack(padx=2, pady=2)

    # Affichage de la fenêtre
    message_win.mainloop()


# Utilisationde la fonction
# create_message_box()
