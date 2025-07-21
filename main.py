import datetime
import subprocess
import os
import tkinter as tk
from dotenv import load_dotenv

import requests


def get_nearest_sunday_on_or_before(date):
    """Trouve le dimanche le plus proche avant ou égal à la date donnée."""
    days_since_sunday = (date.weekday() + 1) % 7
    nearest_sunday = date - datetime.timedelta(days=days_since_sunday)
    return nearest_sunday


def get_nearest_saturday_on_or_after(date):
    """Trouve le samedi le plus proche après ou égal à la date donnée."""
    days_until_saturday = (5 - date.weekday()) % 7
    nearest_saturday = date + datetime.timedelta(days=days_until_saturday)
    return nearest_saturday


def create_drawing_gui(grid_rows, grid_cols):
    """Ouvre une interface graphique pour créer le dessin."""
    cell_size = 15  # Taille de chaque cellule en pixels

    # Initialise la fenêtre tkinter
    root = tk.Tk()
    root.title("Grille de Dessin")

    # Calcule la taille du canvas
    canvas_width = cell_size * grid_cols
    canvas_height = cell_size * grid_rows

    # Crée le canvas
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
    canvas.pack()

    # Initialise le dessin et les rectangles
    drawing = [[0 for _ in range(grid_cols)] for _ in range(grid_rows)]
    rectangles = [[None for _ in range(grid_cols)] for _ in range(grid_rows)]

    # Crée les rectangles sur le canvas
    for row in range(grid_rows):
        for col in range(grid_cols):
            x1 = col * cell_size
            y1 = row * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            rect = canvas.create_rectangle(x1, y1, x2, y2, fill='white', outline='gray')
            rectangles[row][col] = rect

    # Variables pour suivre l'état du clic et du mode de dessin
    is_drawing = False
    drawing_mode = None  # Peut être 'draw' ou 'erase'

    # Fonction pour commencer le dessin
    def start_drawing(event):
        nonlocal is_drawing, drawing_mode
        is_drawing = True
        x, y = event.x, event.y
        col = x // cell_size
        row = y // cell_size
        if 0 <= row < grid_rows and 0 <= col < grid_cols:
            # Détermine le mode de dessin en fonction de l'état initial de la cellule
            if drawing[row][col] == 0:
                drawing_mode = 'draw'
                set_cell(row, col, 1)
            else:
                drawing_mode = 'erase'
                set_cell(row, col, 0)

    # Fonction pour arrêter le dessin
    def stop_drawing(event):
        nonlocal is_drawing, drawing_mode
        is_drawing = False
        drawing_mode = None

    # Fonction pour définir l'état d'une cellule
    def set_cell(row, col, value):
        drawing[row][col] = value
        color = 'black' if value == 1 else 'white'
        canvas.itemconfig(rectangles[row][col], fill=color)

    # Fonction pour dessiner en maintenant le clic
    def draw(event):
        if is_drawing and drawing_mode is not None:
            x, y = event.x, event.y
            col = x // cell_size
            row = y // cell_size
            if 0 <= row < grid_rows and 0 <= col < grid_cols:
                if drawing_mode == 'draw' and drawing[row][col] == 0:
                    set_cell(row, col, 1)
                elif drawing_mode == 'erase' and drawing[row][col] == 1:
                    set_cell(row, col, 0)

    # Lie les événements de la souris aux fonctions correspondantes
    canvas.bind("<ButtonPress-1>", start_drawing)
    canvas.bind("<ButtonRelease-1>", stop_drawing)
    canvas.bind("<B1-Motion>", draw)

    # Bouton pour sauvegarder et quitter
    def save_and_exit():
        root.destroy()

    save_button = tk.Button(root, text="Sauvegarder et Quitter", command=save_and_exit)
    save_button.pack()

    # Démarre la boucle principale
    root.mainloop()

    # Retourne le dessin après la fermeture de la fenêtre
    return drawing


def make_commit(commit_date, file_path):
    """Effectue un commit à une date spécifique."""
    # Crée ou modifie un fichier pour le commit
    with open(file_path, 'a') as f:
        f.write(f"Commit on {commit_date}\n")
    # Définit les variables d'environnement pour la date du commit
    env = os.environ.copy()
    date_str = commit_date.strftime('%Y-%m-%d %H:%M:%S')
    env['GIT_AUTHOR_DATE'] = date_str
    env['GIT_COMMITTER_DATE'] = date_str
    # Ajoute le fichier au staging
    subprocess.run(['git', 'add', file_path], check=True)
    # Effectue le commit
    subprocess.run(['git', 'commit', '-m', f"Commit on {commit_date}"], check=True, env=env)


def get_days_without_commit(username, start_date, end_date, github_token):
    """
    Récupère la liste des jours où un utilisateur GitHub n'a pas fait de commit dans une plage de dates donnée.

    Paramètres:
    - username: Nom d'utilisateur GitHub (str).
    - start_date: Date de début (datetime.date).
    - end_date: Date de fin (datetime.date).
    - github_token: Jeton d'accès personnel GitHub (str).

    Retourne:
    - Une liste d'objets datetime.date représentant les jours sans commit.
    """
    # Convertir les dates au format ISO 8601 avec l'heure
    from_date = start_date.isoformat() + "T00:00:00Z"
    to_date = end_date.isoformat() + "T23:59:59Z"

    # Formuler la requête GraphQL
    query = """
    query ($username: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $username) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """

    variables = {
        "username": username,
        "from": from_date,
        "to": to_date
    }

    headers = {
        "Authorization": f"Bearer {github_token}"
    }

    url = "https://api.github.com/graphql"

    # Envoyer la requête POST
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)

    # Vérifier la réponse
    if response.status_code != 200:
        raise Exception(f"Échec de la requête avec le code de statut {response.status_code}, {response.text}")

    data = response.json()

    # Vérifier les erreurs dans la réponse
    if 'errors' in data:
        raise Exception(f"Erreur dans la requête GraphQL: {data['errors']}")

    # Extraire les jours de contribution
    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']

    no_commit_days = set()

    for week in weeks:
        for day in week['contributionDays']:
            # {'date': '2023-10-08', 'contributionCount': 5}
            # stock day object in contribution_dates if contributionCount is not 0
            if day['contributionCount'] == 0:
                no_commit_days.add(datetime.datetime.strptime(day['date'], '%Y-%m-%d').date())

    return sorted(no_commit_days)


def main():
    # Informations utilisateur
    load_dotenv()
    username = os.getenv("GITHUB_USERNAME")
    token = os.getenv("GITHUB_TOKEN")

    today = datetime.date.today()
    one_year_ago = today - datetime.timedelta(days=365)

    # Détermine les dates de début et de fin pour la grille
    start_date = get_nearest_sunday_on_or_before(one_year_ago)
    print(start_date)
    end_date = get_nearest_saturday_on_or_after(today)
    print(end_date)

    print("Récupération des jours sans commit...")
    days_without_commit = get_days_without_commit(username, start_date, end_date, token)
    print(f"Nombre de jours sans commit : {len(days_without_commit)}")
    print("Remplissage de la grille pour les jours sans commit...")
    for day in days_without_commit:
        print(f"Commit le {day}")
        # make_commit(day, 'commits.txt')
        pass

    # Calcule le nombre de semaines et de jours pour la grille
    delta_days = (end_date - start_date).days + 1  # Inclusif
    grid_cols = (delta_days + 6) // 7  # Nombre de semaines
    grid_rows = 7  # Jours de la semaine

    # Lit le dessin depuis le fichier
    drawing = create_drawing_gui(grid_rows, grid_cols)

    with open('drawing.txt', 'w') as f:
        for row in drawing:
            line = ''.join(['#' if cell else ' ' for cell in row])
            f.write(line + '\n')

        # Pour chaque case remplie, effectue un commit à la date correspondante
        for row in range(grid_rows):
            for col in range(grid_cols):
                if drawing[row][col]:
                    # Calcule la date du commit
                    date = start_date + datetime.timedelta(days=col * 7 + row)
                    # Effectue le commit à cette date
                    print(f"Commit le {date}")
                    # make_commit(date, 'commits.txt')


if __name__ == '__main__':
    main()
