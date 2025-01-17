# monitoring

# Supervision et Monitoring d'Infrastructure Linux

Ce projet fournit une solution simple et efficace pour superviser une infrastructure Linux, en collectant des métriques système via des agents Python et en sauvegardant ces données pour analyse.

---

## 🛠️ Fonctionnalités

### 1. Serveur de Monitoring
- **Endpoints :**
  - `/healthcheck` : Vérifie si l'agent est opérationnel.
  - `/getmetrics` : Récupère les métriques système (CPU, mémoire, disque, etc.).
- Collecte de métriques en temps réel grâce à `psutil`.

### 2. Script de Supervision
- Collecte des métriques de plusieurs agents en parallèle.
- Gestion dynamique des listes blanche et noire :
  - **Liste blanche** : Agents à surveiller.
  - **Liste noire** : Agents inaccessibles ou hors service.
- Sauvegarde des métriques dans un fichier JSON (`metrics_data.json`).

---

## 🖥️ Installation

### Prérequis
1. **Python 3.7+** installé.
2. Bibliothèques Python nécessaires :
   - `psutil`
   - `flask`
   - `requests`
   - `python-dotenv`

### Installation des dépendances
```bash
pip install -r requirements-agent
pip install -r requirements-collector
```

### Configuration

    Créez un fichier .env dans le répertoire principal avec le contenu suivant :

METRICS_FILE=metrics_data.json
INTERVAL_HEALTH_CHECK=3
INTERVAL_METRICS_CHECK=1
WHITELIST_AGENT=127.0.0.1,192.168.1.100
HEALTHROOT=healthcheck
METRICSROOT=getmetrics

### Paramètres principaux :

    METRICS_FILE : Nom du fichier JSON où les métriques seront sauvegardées.
    INTERVAL_HEALTH_CHECK : Intervalle (en secondes) entre les vérifications de santé.
    INTERVAL_METRICS_CHECK : Intervalle (en secondes) entre les collectes de métriques.
    WHITELIST_AGENT : Liste des adresses IP des agents autorisés, séparées par des virgules.


### arborescence
├── agent.py              # Script Flask pour l'agent
├── supervisor.py         # Script de supervision
├── metrics_data.json     # Fichier JSON contenant les métriques collectées
├── .env                  # Variables d'environnement pour la configuration
├── requirements.txt      # Liste des dépendances Python
├── README.md             # Documentation du projet

### auteur
josselin
heidi
antoine