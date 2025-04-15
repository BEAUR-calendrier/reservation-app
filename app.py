from flask import Flask, render_template, request, redirect, jsonify
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# Liste des utilisateurs prédéfinis
USERS = [
    "Emmanuelle", "Eric", "Bastien", "Junior", "Baptiste", "Jules",
    "Christopher", "Guillaume", "Léo", "Charles", "Mathis"
]

# Matériel disponible
MATERIEL = [
    "Station S3", "Station S6", "Station S8", "GPS R10-4", "GPS R10-5", "GPS R10-6",
    "GPS-EMLID", "Scanner Statique", "Scanner dynamique ORBIS", "Drone M3",
    "Drone M300", "Berlingo", "Kangoo", "E-Partner", "208 Philippe", "208 Simone"
]

# Fichier de données
DATA_FILE = 'reservations.json'

# Couleurs prédéfinies par utilisateur
COLORS = [
    '#FF5733', '#33B5FF', '#75FF33', '#FFC133', '#8E44AD', '#E67E22',
    '#16A085', '#34495E', '#D35400', '#2ECC71', '#C0392B'
]
USER_COLORS = dict(zip(USERS, COLORS))

# Création du fichier si inexistant
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

@app.route('/')
def index():
    return render_template('index.html', users=USERS)

@app.route('/available', methods=['POST'])
def available():
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')

    with open(DATA_FILE, 'r') as f:
        reservations = json.load(f)

    reserved_items = set()
    for r in reservations:
        if r['end'] > start and r['start'] < end:
            reserved_items.update(r['items'])

    available_items = [item for item in MATERIEL if item not in reserved_items]
    return jsonify(available_items)

@app.route('/reserve', methods=['POST'])
def reserve():
    name = request.form.get('other_name') or request.form.get('name')
    start = request.form.get('start')
    end = request.form.get('end')
    items = request.form.getlist('items')

    with open(DATA_FILE, 'r') as f:
        reservations = json.load(f)

    reservations.append({
        'id': str(uuid.uuid4()),  # Ajout d'un ID unique
        'name': name,
        'start': start,
        'end': end,
        'items': items
    })

    with open(DATA_FILE, 'w') as f:
        json.dump(reservations, f)

    return redirect('/')

@app.route('/events')
def events():
    with open(DATA_FILE, 'r') as f:
        reservations = json.load(f)

    events = []
    for r in reservations:
        event = {
            'id': r['id'],  # Ajout de l'ID ici
            'title': f"{r['name']} ({', '.join(r['items'])})",
            'start': r['start'],
            'end': r['end'],
            'color': USER_COLORS.get(r['name'], '#888')
        }
        events.append(event)

    return jsonify(events)

@app.route('/update', methods=['POST'])
def update_event():
    data = request.get_json()
    with open(DATA_FILE, 'r') as f:
        reservations = json.load(f)

    for r in reservations:
        if r['id'] == data['id']:
            r['start'] = data['start']
            r['end'] = data['end']
            r['name'] = data['title'].split(' (')[0]  # Optionnel, à adapter si besoin

    with open(DATA_FILE, 'w') as f:
        json.dump(reservations, f)

    return '', 204

@app.route('/delete', methods=['POST'])
def delete_event():
    data = request.get_json()
    with open(DATA_FILE, 'r') as f:
        reservations = json.load(f)

    reservations = [r for r in reservations if r['id'] != data['id']]

    with open(DATA_FILE, 'w') as f:
        json.dump(reservations, f)

    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
