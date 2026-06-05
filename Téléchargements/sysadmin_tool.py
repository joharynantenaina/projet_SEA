import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
import os

# ==========================
# AUTHENTIFICATION
# ==========================

def demander_mdp():
    return simpledialog.askstring("Authentification","Mot de passe administrateur :",show="*")


def verifier_sudo(password):

    resultat = subprocess.run(["sudo", "-S", "-v"],input=password + "\n",text=True,capture_output=True)

    return resultat.returncode == 0


# ==========================
# UTILITAIRES
# ==========================

def changer_page(page):

    for frame in pages.values():
        frame.pack_forget()

    page.pack(fill="both", expand=True)


def afficher(zone, texte):
    zone.insert(tk.END, texte + "\n")
    zone.see(tk.END)


def nettoyer_zone(zone):
    zone.delete("1.0", tk.END)


# ==========================
# ACTIONS
# ==========================

def nettoyage():

    nettoyer_zone(zone_nettoyage)

    mdp = demander_mdp()

    if not mdp:
        return

    if not verifier_sudo(mdp):
        messagebox.showerror("Erreur","Mot de passe incorrect.")
        return

    afficher(zone_nettoyage, "Début du nettoyage...")

    commandes = ["find /tmp /var/tmp ~/.cache /var/cache ~/.local/share/Trash -type f -mtime +7 -delete","find /var/log -name '*.gz' -type f -delete","rm -rf ~/.local/share/Trash/*","apt clean","apt autoremove -y"]

    for commande in commandes:

        afficher(zone_nettoyage,f"Exécution : {commande}")

        subprocess.run(["sudo", "-S", "bash", "-c", commande],input=mdp + "\n",text=True)

    afficher(zone_nettoyage,"\nNettoyage terminé.")


def attenuation():

    nettoyer_zone(zone_cpu)

    try:

        resultat = subprocess.check_output("top -bn1 | grep '%Cpu'",shell=True,text=True)

        idle = float(resultat.split()[7].replace(",", "."))

        charge = 100 - idle

        afficher(zone_cpu,f"Charge CPU : {charge:.2f}%")

        if charge > 50:

            afficher(zone_cpu,"CPU fortement chargé.")

        else:

            afficher(zone_cpu,"Le CPU n'est pas surchargé.")

    except Exception as e:

        afficher(zone_cpu, str(e))


def config_espace():

    nettoyer_zone(zone_espace)

    mdp = demander_mdp()

    if not mdp:
        return

    if not verifier_sudo(mdp):
        messagebox.showerror("Erreur","Mot de passe incorrect.")
        return

    groupe = entree_groupe.get().strip()
    dossier = entree_dossier.get().strip()

    if not groupe or not dossier:

        messagebox.showwarning("Information","Veuillez remplir tous les champs.")
        return

    try:

        subprocess.run(["sudo", "-S", "addgroup", groupe],input=mdp + "\n",text=True)

        subprocess.run(["sudo", "-S", "chown", f":{groupe}", dossier],input=mdp + "\n",text=True)

        subprocess.run(["sudo", "-S", "chmod", "770", dossier],input=mdp + "\n",text=True)

        afficher(zone_espace,"Configuration terminée.")

    except Exception as e:

        afficher(zone_espace, str(e))


def config_env():

    nettoyer_zone(zone_env)

    variable = entree_variable.get().strip()
    valeur = entree_valeur.get().strip()

    if not variable or not valeur:

        messagebox.showwarning("Information","Veuillez remplir tous les champs.")
        return

    try:

        bashrc = os.path.expanduser("~/.bashrc")

        with open(bashrc,"a") as fichier:

            fichier.write(f"\nexport {variable}={valeur}\n")

        afficher(zone_env,f"Variable ajoutée : {variable}={valeur}")

    except Exception as e:

        afficher(zone_env, str(e))


# ==========================
# FENETRE PRINCIPALE
# ==========================

fenetre = tk.Tk()

fenetre.title("Récupération et Initialisation du Système")

fenetre.geometry("800x600")

pages = {}

# ==========================
# MENU PRINCIPAL
# ==========================

menu = tk.Frame(fenetre)

pages["menu"] = menu

tk.Label(menu,text="Récupération et Initialisation du Système",font=("Arial", 16, "bold")).pack(pady=20)

tk.Button(menu,text="1. Nettoyage système",width=40,command=lambda:changer_page(page_nettoyage)).pack(pady=5)

tk.Button(menu,text="2. Atténuation CPU",width=40,command=lambda:changer_page(page_cpu)).pack(pady=5)

tk.Button(menu,text="3. Configuration espace",width=40,command=lambda:changer_page(page_espace)).pack(pady=5)

tk.Button(menu,text="4. Variables d'environnement",width=40,command=lambda:changer_page(page_env)).pack(pady=5)

# ==========================
# PAGE NETTOYAGE
# ==========================

page_nettoyage = tk.Frame(fenetre)

pages["nettoyage"] = page_nettoyage

tk.Label(page_nettoyage,text="Nettoyage système",font=("Arial", 14)).pack(pady=10)

tk.Button(page_nettoyage,text="Lancer le nettoyage",command=nettoyage).pack()

zone_nettoyage = tk.Text(page_nettoyage,height=20)

zone_nettoyage.pack(fill="both",expand=True,padx=10,pady=10)

tk.Button(page_nettoyage,text="Retour",command=lambda:changer_page(menu)).pack(pady=10)

# ==========================
# PAGE CPU
# ==========================

page_cpu = tk.Frame(fenetre)

pages["cpu"] = page_cpu

tk.Label(page_cpu,text="Atténuation CPU",font=("Arial", 14)).pack(pady=10)

tk.Button(page_cpu,text="Analyser",command=attenuation).pack()

zone_cpu = tk.Text(page_cpu,height=20)

zone_cpu.pack(fill="both",expand=True,padx=10,pady=10)

tk.Button(page_cpu,text="Retour",command=lambda:changer_page(menu)).pack(pady=10)

# ==========================
# PAGE ESPACE
# ==========================

page_espace = tk.Frame(fenetre)

pages["espace"] = page_espace

tk.Label(page_espace,text="Configuration espace",font=("Arial", 14)).pack(pady=10)

tk.Label(page_espace,text="Nom du groupe").pack()

entree_groupe = tk.Entry(page_espace)
entree_groupe.pack()

tk.Label(page_espace,text="Chemin du dossier").pack()

entree_dossier = tk.Entry(page_espace)
entree_dossier.pack()

tk.Button(page_espace,text="Configurer",command=config_espace).pack(pady=10)

zone_espace = tk.Text(page_espace,height=15)

zone_espace.pack(fill="both",expand=True,padx=10,pady=10)

tk.Button(page_espace,text="Retour",command=lambda:changer_page(menu)).pack(pady=10)

# ==========================
# PAGE ENV
# ==========================

page_env = tk.Frame(fenetre)

pages["env"] = page_env

tk.Label(page_env,text="Variables d'environnement",font=("Arial", 14)).pack(pady=10)

tk.Label(page_env,text="Nom de la variable").pack()

entree_variable = tk.Entry(page_env)
entree_variable.pack()

tk.Label(page_env,text="Valeur").pack()

entree_valeur = tk.Entry(page_env)
entree_valeur.pack()

tk.Button(page_env,text="Ajouter",command=config_env).pack(pady=10)

zone_env = tk.Text(page_env,height=15)

zone_env.pack(fill="both",expand=True,padx=10,pady=10)

tk.Button(page_env,text="Retour",command=lambda:changer_page(menu)).pack(pady=10)

# ==========================
# DEMARRAGE
# ==========================

changer_page(menu)

fenetre.mainloop()