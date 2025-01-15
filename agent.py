import psutil
from flask import Flask, jsonify
import platform

app = Flask(__name__)

def collect_metrics():
    """
    Collecte des métriques système.
    """
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    os = platform.system()
    hostname = platform.node()

    metrics = {
        "cpu_usage": f"{cpu_usage}%",
        "memory_usage": f"{memory}%",
        "disk_usage": f"{disk}%",
        "os": os,
        "hostname": hostname
    }
    return metrics

@app.route('/metrics', methods=['GET'])
def send_metrics():
    """
    Renvoie les métriques collectées au collecteur.
    """
    metrics = collect_metrics()
    return jsonify(metrics)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
