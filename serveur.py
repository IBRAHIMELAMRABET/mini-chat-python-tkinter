# -----------------------------------------------------
# mini projet programme client / seveur
# this is the part of the server
# ibrahime lamrabet  &&  khawla haddani
# gui : Graphical User Interface
# -----------------------------------------------------zz

import sqlite3
import threading
import socket
import tkinter as tk
import tkinter.messagebox
import tkinter.scrolledtext


# Établir la connexion à la base de données et créer la table si elle n'existe pas
conn = sqlite3.connect('my.db', check_same_thread=False)
print("Connexion réussie à SQLite") 
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS client (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        address TEXT,
        date DEFAULT CURRENT_TIMESTAMP
);''')
cur.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emeteur TEXT,
        recepteur TEXT,
        message TEXT,
        date DEFAULT CURRENT_TIMESTAMP
);''')





# Configurer la liste des clients et la liste des noms
clients = []
noms = []


# créer les functions


# Envoi d'un message à tous les clients connectés
def messaging(message):
    try:
        for client in clients:
           client.send(message)
    except OSError:
        # Si le socket est fermé, supprimer le client de la liste
            clients.remove(client) 
            client.close()


# Récupérer l'historique des messages de la base de données
def handle_history_request():
    cur.execute("SELECT date,recepteur,message date FROM messages")
    rows = cur.fetchall()
    history = ""
    for row in rows:
        history += str(row) + '\n'   
    conn.commit()
    return history


# Insérer un message dans la table des messages de la base de données
def insert_message(sender, receiver, message):
    cur.execute("INSERT INTO messages(emeteur, recepteur, message) VALUES(?, ?, ?)", (sender, receiver, message))
    conn.commit()


# Traitement des requêtes du client
def traitement(client):
    while True:
        try:
            requete_client = client.recv(2048).decode('utf-8')

            index = requete_client[0]
            message = requete_client[1:]
            message_requete = ''.join(message)
            
            if  index == '1':
                 history=handle_history_request()
                 client.send(f"1{history}".encode('utf-8'))
            elif index == '2':
                liste = liste_clients()
                client.send(f"2{liste}".encode('utf-8'))
            elif index == '3':
                messaging(f"3{message_requete}".encode('utf-8'))
            
            # Enregistrement du message dans la base de données
            emeteur = noms[clients.index(client)]
            for recepteur in noms:
                if recepteur != emeteur:
                    insert_message(emeteur, recepteur, message)
        # Suppression du client de la liste des clients connectés
        except:
            if client in clients:
                index = clients.index(client)
                nom = noms[index]
                messaging(f'3{nom} déconecte ! \n '.encode('utf-8'))
                tkinter.messagebox.showinfo(
                "Client Disconnected", "{} disconnected!".format(nom))
                output_widget.insert(tk.END, '{} disconnected!\n'.format(nom))
                noms.remove(nom)
                client_list.delete(0, tk.END) 
                for nom in noms:
                    client_list.insert(tk.END, nom)


# Créer une liste des noms de tous les clients connectés
def liste_clients():
    liste = '\n'.join(noms)
    return liste               


#Réception des connexions des clients
def reception():
    
    while True:
        
        client, address=server.accept()
        print("connecter a : ", address)
        output_widget.insert(tk.END, 'Connected to: {}\n'.format(address))
        client.send('0prenom'.encode('utf-8'))
        nom = client.recv(2048).decode('utf-8')
        noms.append(nom)
        
        client_list.delete(0, tk.END) 
        for nom in noms:
                client_list.insert(tk.END, nom) 
        try:
            cur.execute("INSERT INTO client(nom ,address) VALUES(? , ?)",
                      (str(nom), str(address)))
            conn.commit()
        except sqlite3.Error as e:
            print(f'An error occurred: {e}')
        # Ajout du client à la liste des clients 
        clients.append(client)
        print("le nom is {} \n".format(nom))
        messaging("3{} joined! \n ".format(nom).encode('utf-8'))
        client.send('3Connected to server! \n '.encode('utf-8'))
        tkinter.messagebox.showinfo("Client Connected", "{} connected!".format(nom))
        output_widget.insert(tk.END, '{} connected!\n'.format(nom))
        # Démarrage d'un thread pour gérer les requêtes du client
        thread = threading.Thread(target=traitement, args=(client,))
        thread.start()



#envoyer des message from the server to the clients
def send_message(text):
    message = text.get()
    messaging('3 serveur : {}'.format(message).encode('utf-8') + b'\n')
    output_widget.insert(tk.END, 'Serveur: {}\n'.format(message))        


# Initialisation de l'interface utilisateur
root = tk.Tk()
root.title("Chat Server")
root.configure(bg="#9898f5")
root.geometry("450x550")

# creer une fenetre
output_widget = tkinter.scrolledtext.ScrolledText(root, state='normal')
output_widget.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# la zone d entrer et le envoie button
entry_field = tk.Entry(root)
entry_field.pack(side=tk.LEFT, fill=tk.X,padx=2, expand=True)
send_button = tk.Button(
    root, text="Send", command=lambda: send_message(entry_field))
send_button.pack(side=tk.LEFT)

# creer une liste des clients connectés
client_list = tk.Listbox(root)
client_list.pack(side=tk.RIGHT, fill=tk.Y)
client_list.insert(tk.END, "Les clients connectées : \n")


# Démarrage du serveur
nom_pc = socket.gethostname()
host = socket.gethostbyname(nom_pc)
print(host)
addr = (host, 12345)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(addr)
server.listen()
output_widget.insert(tk.END, 'le serveur comencer !!\n')

# Démarrage de la réception des connexions des clients
reception_thread = threading.Thread(target=reception)
reception_thread.start()

# cur.execute("SELECT * FROM messages")
# print(cur.fetchall())

root.mainloop()