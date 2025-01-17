#!/usr/bin/python3
"""
Ce script expose un serveur Flask qui collecte des métriques système et les rend disponibles via un endpoint `/getmetrics`.
Les métriques incluent l'utilisation du CPU, de la mémoire, du disque, le nom du système d'exploitation,
le nom de l'hôte, et l'heure.

Le port d'exécution du serveur doit etre choisis par l'ingénieur sinon le port par defaut est de 5000

Les métriques sont collectées en temps réel à l'aide de la bibliothèque `psutil`.
"""

import psutil
from flask import Flask, jsonify
import platform
from datetime import datetime

# Initialisation de l'application Flask
app = Flask(__name__)

def collect_metrics():
    """
    Collecte les métriques système, incluant l'utilisation du CPU, de la mémoire, et du disque, 
    ainsi que des informations sur le système d'exploitation et le nom de l'hôte.

    Returns:
    - dict: Un dictionnaire contenant les métriques collectées :
        - cpu_usage (str): Pourcentage d'utilisation du CPU.
        - memory_usage (str): Pourcentage d'utilisation de la mémoire.
        - disk_usage (str): Pourcentage d'utilisation du disque principal.
        - os (str): Nom du système d'exploitation.
        - hostname (str): Nom de l'hôte de la machine.
        - timestamp (str): Horodatage actuel au format ISO 8601.
    """
    # Collecte des métriques système
    cpu_usage = psutil.cpu_percent(interval=1)  # Utilisation CPU en pourcentage
    memory = psutil.virtual_memory().percent  # Utilisation mémoire en pourcentage
    disk = psutil.disk_usage('/').percent  # Utilisation disque en pourcentage
    os_name = platform.system()  # Nom du système d'exploitation
    hostname = platform.node()  # Nom de la machine (hôte)
    timestamp = datetime.now().isoformat()  # Horodatage actuel

    # Création du dictionnaire contenant les métriques
    metrics = {
        "cpu_usage": f"{cpu_usage}%",
        "memory_usage": f"{memory}%",
        "disk_usage": f"{disk}%",
        "os": os_name,
        "hostname": hostname,
        "timestamp": timestamp
    }
    return metrics

@app.route('/healthcheck', methods=['GET'])
def provide_health():
     """
    Endpoint Flask pour fournir un healthcheck.
    Lorsqu'une requête POST est reçue sur `/healthcheck`, les métriques système sont collectées et renvoyées en JSON.

    Returns:
    - tuple: Un tuple contenant :
        - Response: La réponse JSON avec les métriques.
        - int: Le code HTTP 200 (succès).
    """
     return jsonify('OK'),200

@app.route('/getmetrics', methods=['GET'])
def provide_metrics():
    """
    Endpoint Flask pour fournir les métriques collectées.
    Lorsqu'une requête POST est reçue sur `/getmetrics`, les métriques système sont collectées et renvoyées en JSON.

    Returns:
    - tuple: Un tuple contenant :
        - Response: La réponse JSON avec les métriques.
        - int: Le code HTTP 200 (succès).
    """
    # Collecte des métriques système
    metrics = collect_metrics()
    # Renvoi des métriques en réponse à la requête
    return jsonify(metrics), 200

if __name__ == '__main__':
    """
    Point d'entrée principal du script.
    Configure et lance le serveur Flask sur l'adresse `0.0.0.0` et le port 5000 par defaut
    """
    # Lancement de l'application Flask
    app.run(host='0.0.0.0', port=5000)

