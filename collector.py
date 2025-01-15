from flask import Flask, jsonify
import requests
import json


app = Flask(__name__)

# Fichier où les métriques seront sauvegardées
METRICS_FILE:str= 'metrics_data.json'


intervalle:int = 10



# Fonction pour sauvegarder les données dans un fichier
def save_metrics(metrics):

    with open(METRICS_FILE, 'a') as f:
        json.dump(metrics, f, indent=4)


@app.route('/getmetrics', methods=['GET'])
def send_getmetrics():
    # Envoi des métriques au collecteur via HTTP
        agent_url = "http://172.21.31.251:5001/getmetrics"
        headers = {'Content-Type': 'application/json'}
        response = requests.post(agent_url, data=json.dumps('getmetrics'), headers=headers)
        print(f"Envoi de la demande getmetrics : {response.status_code}")
        if response.status_code == 200:
            if not response.json() :
                return jsonify({"error": "No data received"}), 400
            else:
                save_metrics(response.json())
                return print('getmetrics succes 200')

send_getmetrics()
# Route principale pour afficher un message de bienvenue
@app.route('/')
def index():
    return "Collecteur de métriques en ligne!"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
