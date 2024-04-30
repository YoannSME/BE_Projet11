from tkinter import *

# Fonctions qui permettent de modifier l'état de brouillard d'une image
def switch_to_brouillard():
    a = 4
    print(a)


def switch_to_not_brouillard():
    b = 1
    print(b)


def switch_to_indetermine():
    c = 5
    print(c)


def create_message_box():
    # Création de la fenêtre de message
    message_win = Tk()
    message_win.minsize(300, 100)
    message_win.maxsize(300, 100)
    message_win.title('Etat du brouillard')
    message_win.iconbitmap("montagne_icon.ico")
    Label(message_win, text="Quel est l'état du brouillard ?").pack(padx=0, pady=1)

    # Création des boutons
    bouton1 = Button(message_win, text='Brouillard', command=switch_to_brouillard)
    bouton2 = Button(message_win, text='Pas de brouillard', command=switch_to_not_brouillard)
    bouton3 = Button(message_win, text='Indeterminé', command=switch_to_indetermine)

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
