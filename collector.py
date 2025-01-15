from flask import Flask, request, jsonify
import json
import requests
from datetime import datetime

app = Flask(__name__)

# Fichier où les métriques seront sauvegardées
METRICS_FILE = 'metrics_data.json'
AGENT_URL = 'http://172.21.31.251:5001/metrics'

def load_metrics():
    """
    Charge les métriques sauvegardées depuis un fichier.
    """
    try:
        with open(METRICS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_metrics(metrics):
    """
    Sauvegarde les métriques dans un fichier JSON.
    """
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=4)

@app.route('/getmet', methods=['GET'])
def get_metrics():
    """
    Envoie une requête à l'agent pour récupérer les métriques.
    """
    try:
        response = requests.get(AGENT_URL)
        if response.status_code == 200:
            data = response.json()

            # Ajoute un horodatage aux métriques
            timestamp = datetime.now().isoformat()
            metrics = load_metrics()
            metrics[timestamp] = data
            save_metrics(metrics)

            return jsonify({"status": "success", "metrics": data, "timestamp": timestamp}), 200
        else:
            return jsonify({"error": f"Échec de la requête à l'agent. Code HTTP : {response.status_code}"}), 500
    except requests.RequestException as e:
        return jsonify({"error": f"Erreur lors de la requête à l'agent : {str(e)}"}), 500
@app.route('/')
def index():
    return "Collecteur de métriques en ligne!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
