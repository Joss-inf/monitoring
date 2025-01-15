import psutil
from flask import Flask, jsonify
import platform
from datetime import datetime
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
    timestamp = datetime.now().isoformat()
    
    metrics = {
        "cpu_usage": f"{cpu_usage}%",
        "memory_usage": f"{memory}%",
        "disk_usage": f"{disk}%",
        "os": os,
        "hostname": hostname,
        "timestapm":timestamp
    }
    return metrics

@app.route('/getmetrics', methods=['POST'])
def provide_metrics():
    """
    Renvoie les métriques collectées lorsque le collecteur les demande.
    """
    metrics = collect_metrics()
    return jsonify(metrics), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
