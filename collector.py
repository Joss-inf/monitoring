#!/usr/bin/python3

"""
Ce script exécute des vérifications de santé et des récupérations de métriques pour une liste d'agents,
et enregistre ces données dans un fichier JSON. Les vérifications sont effectuées à intervalles réguliers
avec un mécanisme asynchrone pour gérer plusieurs agents simultanément.

Le script vérifie la santé des agents via l'endpoint /healthcheck et récupère les métriques via l'endpoint /metrics.
Les agents sont spécifiés dans un fichier d'environnement (.env) et sont gérés par des listes blanches et noires dynamiques.

Les données collectées sont enregistrées dans un fichier JSON, et des notifications sont émises en cas de problème de connectivité.
"""

from datetime import datetime
import asyncio
import requests
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Fonction pour vérifier si une valeur est positive
def check_positive(value: int) -> bool:
    """
    Vérifie si une valeur est positive.

    Args:
    - value (int): La valeur à vérifier.

    Returns:
    - bool: True si la valeur est positive, sinon False.
    """
    try:
        return value > 0
    except ValueError:
        return False

# Lecture des variables d'environnement
METRICS_FILE:str = os.getenv('METRICS_FILE', 'metrics_data.json')  # Fichier où les métriques sont sauvegardées
INTERVAL_HEALTH_CHECK:int = int(os.getenv('INTERVAL_HEALTH_CHECK', 3))  # Intervalle pour les vérifications de santé (en secondes)
INTERVAL_METRICS_CHECK:int = int(os.getenv('INTERVAL_METRICS_CHECK', 1))  # Intervalle pour la récupération des métriques (en secondes)
HEALTHROOT:str = os.getenv('HEALTHROOT', 'healthcheck')  # Chemin de l'endpoint de vérification de santé
METRICSROOT:str = os.getenv('METRICSROOT', 'metrics')  # Chemin de l'endpoint des métriques

# Vérification que les intervalles sont des entiers positifs
if not check_positive(INTERVAL_HEALTH_CHECK) or not check_positive(INTERVAL_METRICS_CHECK):
    raise ValueError("INTERVAL_HEALTH_CHECK et INTERVAL_METRICS_CHECK doivent être des entiers positifs")

# Lecture de la variable WHITELIST_AGENT et conversion en un ensemble
whitelist_agent_str:str = os.getenv('WHITELIST_AGENT', '')
if whitelist_agent_str:
    WHITELIST_AGENT = set(whitelist_agent_str.split(','))
else:
    raise ValueError("WHITELIST_AGENT est vide")

# BLACKLIST_AGENT reste un ensemble vide par défaut
BLACKLIST_AGENT = set()
TIMESTAMP = datetime.now().isoformat()  # Date et heure actuelles au format ISO

# Fonction pour sauvegarder les données dans un fichier
def save_metrics(ip, info):
    """
    Sauvegarde les métriques pour un agent dans le fichier JSON.

    Args:
    - ip (str): L'adresse IP de l'agent.
    - info (dict): Les informations (métriques) à sauvegarder.
    """
    try:
        with open(METRICS_FILE, 'r') as f:
            metrics = json.load(f)
    except FileNotFoundError:
        print(f'fichier {METRICS_FILE} non existant')
        metrics = {}
    except json.JSONDecodeError:
        print(f"Le fichier {METRICS_FILE} est vide ou corrompu. Réinitialisation.")
        metrics = {}

    # Ajouter l'IP si elle n'existe pas encore dans le fichier
    if ip not in metrics:
        metrics[ip] = []

    # Ajouter les nouvelles informations pour l'IP
    metrics[ip].append(info)

    # Sauvegarder les nouvelles données dans le fichier
    try:
        with open(METRICS_FILE, 'w') as f:
            json.dump(metrics, f, indent=4)
    except FileNotFoundError:
        print(f'fichier {METRICS_FILE} non existant')
    except json.JSONDecodeError:
        print(f"Le fichier {METRICS_FILE} est vide ou corrompu. Impossible de sauvegarder")

# Fonction pour envoyer une requête de vérification de santé à un agent
def get_healthcheck(agent_url: str)->int:
    """
    Envoie une requête GET à l'agent pour vérifier sa santé.

    Args:
    - agent_url (str): L'URL de l'agent à interroger.

    Returns:
    - int: Le code de statut HTTP retourné par l'agent.
    """
    try:
        res = requests.get(f'http://{agent_url}/{HEALTHROOT}', timeout=5)  # Timeout de 5 secondes
        print(f'health_check status code: {res.status_code} from agent: {agent_url}')
        return res.status_code
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête de santé pour {agent_url}: {str(e)}")
        return 500

# Fonction pour récupérer les métriques d'un agent
def get_metrics(agent_url):
    """
    Récupère les métriques d'un agent et les sauvegarde dans le fichier JSON.

    Args:
    - agent_url (str): L'URL de l'agent à interroger.
    """
    try:
        response = requests.get(f'http://{agent_url}/{METRICSROOT}')
        if response.status_code == 200:
            if not response.json():
                return print("Error, No data received", 400)
            else:
                save_metrics(agent_url, response.json())
                return print(f"get metrics success, data received and saved from agent: {agent_url}", 200)
    except requests.exceptions.RequestException as e:
        return print({"error": str(e)}), 500

# Fonction pour vérifier la santé de tous les agents dans la liste blanche
def health_check():
    """
    Effectue une vérification de santé pour chaque agent dans la liste blanche (WHITELIST_AGENT).
    Si un agent échoue, il est ajouté à la liste noire (BLACKLIST_AGENT).
    """
    for agent in WHITELIST_AGENT:
        res = get_healthcheck(str(agent))
        log = {"Health_check_status": res, "timestamp": TIMESTAMP.split('.')[0]}
        if res != 200 and agent not in BLACKLIST_AGENT:
            BLACKLIST_AGENT.add(agent)
        elif res == 200 and agent in BLACKLIST_AGENT:
            BLACKLIST_AGENT.remove(agent)

        save_metrics(agent, log)

# Fonction pour récupérer les métriques de tous les agents dans la liste blanche
def metrics_check():
    """
    Récupère les métriques pour chaque agent dans la liste blanche (WHITELIST_AGENT),
    à condition que l'agent ne soit pas dans la liste noire.
    """
    for agent in WHITELIST_AGENT:
        if agent not in BLACKLIST_AGENT:
            get_metrics(agent)

# Tâche asynchrone pour effectuer des vérifications de santé à intervalles réguliers
async def interval_health_check():
    while True:
        health_check()
        await asyncio.sleep(INTERVAL_HEALTH_CHECK)  # Attente avant la prochaine vérification

# Tâche asynchrone pour récupérer les métriques à intervalles réguliers
async def interval_metrics_check():
    while True:
        metrics_check()
        await asyncio.sleep(INTERVAL_METRICS_CHECK)  # Attente avant la prochaine récupération

# Fonction principale asynchrone qui exécute les deux tâches en parallèle
async def main():
    await asyncio.gather(interval_health_check(), interval_metrics_check())

# Exécution du programme
if __name__ == '__main__':
    asyncio.run(main())
