import socket 
import threading
from threading import Thread
import tkinter as tk
from tkinter import Tk, Label, Entry, Button
import tkinter.scrolledtext
from tkinter import simpledialog
from tkinter import ttk


HOST = '192.168.1.107'
PORT = 12345
addr = (HOST, PORT)


# Fonction pour envoyer un message
def send():
    message = f"{nom}: {input_area.get('1.0','end')}"
    client.send(f'3{message}'.encode('utf-8'))
    input_area.delete('1.0', 'end')

 
# Fonction pour recevoir les messages

def reception():
    while True :
        try:
            requete_server = client.recv(2048).decode('utf-8')
    
            index = requete_server[0]
            message = requete_server[1:]
            message_requete = ''.join(message)
            if index == '0':
                client.send(nom.encode('utf-8'))
            elif index == '1':
                show_history(message)
            elif index == '2':
                clients(message)
            elif index == '3':
                chat_historie.config(state='normal')
                chat_historie.insert('end', message_requete)
                chat_historie.yview('end')
                chat_historie.config(state='disabled')
        except:
            print("An error occured!")
            client.close()
            break

# Fonction pour fermer la fenêtre
def stop():
    client.close()
    fenetre.destroy()
    
# Fonction pour demander l'historique des messages
def handle_history_request():
    client.send('1'.encode('utf-8'))
    
# Fonction pour afficher l'historique des messages
def show_history(history):
    history_window = tkinter.Toplevel(fenetre)
    history_window.configure(bg="#9898f5")
    history_text = tkinter.scrolledtext.ScrolledText(history_window)
    history_text.pack(padx=20, pady=5)
    history_text.insert('end', history + '\n')
    

# Fonction pour demander la liste des clients connectés
def demander_liste_clients():
    client.send("2".encode('utf-8'))

# Fonction pour afficher la liste des clients connectés
def clients(liste):
    fenetre_clients = tk.Tk()
    fenetre_clients.configure(bg="#9898f5")
    fenetre_clients.geometry("400x300")
    clients_text = tkinter.scrolledtext.ScrolledText(fenetre_clients)
    clients_text.insert('end', "Liste des clients connectés:\n\n")
    clients_text.insert('end', liste + "\n\n")
    clients_text.pack(padx=20, pady=5)
    fenetre_clients.mainloop()


# Création de la socket client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Demande de saisir le nom de l'utilisateur
nom = simpledialog.askstring( "nom", "Enter your name:")

# Initialisation de la fenêtre principale
fenetre = tkinter.Tk()
fenetre.configure(bg="#9898f5")

# Création de l'étiquette pour le titre
chat_label = tkinter.Label(fenetre, text="MiniChat",font=("Courier", 15,'bold') , bg="#9898f5")
chat_label.grid(row=0, column=0, columnspan=2, padx=20, pady=5)

# Création du bouton pour afficher l'historique des messages
history_button = ttk.Button(fenetre, text="Historique", command=handle_history_request)
history_button.grid(row=1, column=0, padx=20, pady=5, sticky='w')

# Création du bouton pour afficher la liste des clients connectés
bouton_clients = ttk.Button(
    fenetre, text="Les clients connectés",  command=demander_liste_clients)
bouton_clients.grid(row=1, column=1, padx=20, pady=5, sticky='e')

# Création de la zone de saisie pour les messages
chat_historie = tkinter.scrolledtext.ScrolledText(fenetre)
chat_historie.grid(row=2, column=0, columnspan=2, padx=20, pady=5)
chat_historie.config(state='disabled')


msg_label = tkinter.Label(fenetre, text="Message :",font=("Courier", 15 ,'bold'), bg="#9898f5")
msg_label.grid(row=3, column=0, columnspan=2, padx=20, pady=5)

# création de entrer espace
input_area = tkinter.Text(fenetre, height=4)
input_area.grid(row=4, column=0, columnspan=2, padx=20, pady=5)

# Création du bouton pour envoyer les messages
send_button = ttk.Button(fenetre, text="Envoyer", command=send)
send_button.grid(row=5, column=0, columnspan=2, padx=20, pady=5)
running = True

# conecter avec l addr (host +port)du serveur
client.connect(addr)
recep_thread = threading.Thread(target=reception)
recep_thread.start()

fenetre.protocol("WM_DELETE_WINDOW", stop)
fenetre.mainloop()
