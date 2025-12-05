# Serveur API

Ce dépôt contient une API FastAPI pour la gestion de ressources réseau (hosts, serveurs, entreprises), l'exécution d'actions configurées, et la collecte de résultats de scans (ports, reachability). Le fichier principal est `main.py`.

## Table des matières

- Installation
- Lancement
- Architecture et composants
- Endpoints principaux
- Tâches en arrière-plan
- Export et statistiques
- Limitations et recommandations
- Dépannage


## Installation

1. Créez un environnement virtuel et installez les dépendances :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Si vous ne disposez pas d'un `requirements.txt` complet, installez au minimum :

```bash
pip install fastapi uvicorn sqlmodel sqlalchemy pydantic
```

Remarque pour les containers : si vous utilisez des commandes système comme `ping`, installez le paquet adapté (Debian/Ubuntu) :

```bash
apt-get update && apt-get install -y iputils-ping
```


## Lancement

Démarrer le serveur en développement :

```bash
uvicorn main:app --reload
```

API disponible par défaut sur `http://127.0.0.1:8000`.


## Architecture et composants

- `main.py` : point d'entrée FastAPI. Contient :
  - Endpoints REST CRUD pour `Host`, `Action`, `Indicator`, `Serveur`, `Entreprise`.
  - Fonctions de scan (`ping`, `scan_ports`, `scan_reseau`) et stockage des `ScanResult` en base.
  - Tâches en arrière-plan via `ThreadPoolExecutor` (registry `tasks`).
- `database.py` : configuration de la base (création `engine`, etc.).
- `models/` : définitions SQLModel pour `Host`, `Action`, `Indicator`, `Serveur`, `Entreprise`, `ScanResult`.


## Endpoints principaux (sélection)

Note : les chemins et comportements sont définis dans `main.py` ; voici un résumé utile.

- GET /health
  - Health check basique.

- Hosts
  - GET /hosts — liste tous les hosts.
  - GET /host/{host_id} — récupère un host.
  - POST /host — crée un host (body = Host).
  - PUT /host/{host_id} — met à jour un host.
  - DELETE /host/{host_id} — supprime un host.
  - GET /hosts/by_ip/{ip} — récupérer un host par adresse IP.

- Actions
  - GET /actions
  - GET /action/{action_id}
  - POST /action
  - PUT /action/{action_id}
  - DELETE /action/{action_id}
  - POST /action/{action_id}/run_on_host/{host_id} — exécute `Action.script_path` sur l'IP du host (en tâche de fond). Retourne `task_id`.

- Entreprises / Serveurs
  - CRUD standard : /entreprises, /entreprise/{id}, /serveurs, /serveur/{id}, etc.

- Indicateurs
  - GET /host/{host_id}/indicators
  - POST /host/{host_id}/indicator
  - DELETE /indicator/{indicator_id}
  - DELETE /host/{host_id}/indicator/{indicator_id}

- Scans & Réseau
  - GET /ping/{ip} — effectue un ping (essaie la commande système `ping`, sinon fallback TCP sur ports 80/443/22). Stocke un `ScanResult`.
  - GET /scan/{ip} — scan réseau. Accepte IP ou CIDR ; si donné une IP simple, la route ajoute `/24` par défaut. Itère les hôtes et appelle `ping` pour chacun (attention performance).
  - GET /scan_ports/{ip}?ports=1-1024 — scan synchronisé des ports (range default 1-1024).
  - POST /scan_ports_async/{ip} — lance un scan de ports en tâche de fond et retourne `task_id`.
  - GET /scans/{scan_id} — récupère un `ScanResult`.
  - GET /scans/recent?n=10 — scans récents (par défaut 10).

- Tâches et export
  - GET /tasks/{task_id} — statut et résultat d'une tâche (scan ou exécution d'action) lancée en arrière-plan.
  - GET /stats — quelques statistiques (total hosts, total scans, top ports vus).
  - GET /export/scan/{scan_id}?format=json|csv — export d'un scan (CSV ou JSON). CSV produit une ligne par port ouvert.


## Format des modèles (rappel)

- ScanResult
  - id : int
  - host_id : Optional[int]
  - date : datetime
  - open_ports : JSON/dict

- Host, Action, Indicator, Serveur, Entreprise
  - Voir dossier `models/` pour la définition exacte (SQLModel classes).


## Exemples d'utilisation

- Lancer un scan de ports asynchrone :

```bash
curl -X POST http://127.0.0.1:8000/scan_ports_async/192.0.2.10
# réponse: {"task_id":"..."}

curl http://127.0.0.1:8000/tasks/<task_id>
```

- Exporter un scan en CSV :

```bash
curl -OJ "http://127.0.0.1:8000/export/scan/12?format=csv"
```

- Démarrer une action configurée sur un host (exécutera `script_path` du `Action` avec l'IP du host) :

```bash
curl -X POST http://127.0.0.1:8000/action/5/run_on_host/3
# réponse: {"task_id":"..."}
```


## Limitations, sécurité et performance

1. Permissions réseau
   - L'usage d'ICMP (`ping`) et de paquets bruts (scapy) peut nécessiter des droits root. Dans des containers, installez `iputils-ping` si vous utilisez la commande système `ping`.

2. Performances
   - `scan_reseau` et `scan_ports` sont synchrones et peuvent être très lents sur de grands réseaux ou plages de ports. Les scans asynchrones / ThreadPoolExecutor doivent être utilisés pour réduire le blocage d'API.
   - `scan_reseau` appelle `ping` pour chaque hôte et stocke un `ScanResult` par hôte ; faites attention à la croissance de la base.

3. Sécurité
   - Exécution de scripts via `Action.script_path` : assurez-vous que seuls des scripts sûrs sont référencés et que les appels sont contrôlés (authentification/autorisation). L'API actuelle ne possède pas d'authentification.
   - Validez et nettoyez toutes les entrées utilisateur (IPs, ranges, etc.).

4. Concurrence et ressources
   - Le ThreadPoolExecutor par défaut est limité; surveillez l'utilisation des fichiers/sockets si vous lancez de nombreux scans simultanés.


## Dépannage courant

- Erreur `FileNotFoundError: [Errno 2] No such file or directory: 'ping'` : installer `iputils-ping` ou laisser le fallback TCP agir.
- `ModuleNotFoundError: No module named 'fastapi'` : installez les dépendances via `pip install -r requirements.txt`.
- Problèmes de permissions pour scapy/ICMP : exécutez en tant que root ou donnez les capacités nécessaires au container (ex: `--cap-add=NET_RAW`).


## Docker

Un Dockerfile et un `docker-compose.yml` ont été ajoutés pour exécuter l'application dans un conteneur.

Build et run avec Docker :

```bash
# construction de l'image
docker build -t serveur-app:latest .

# exécution (expose le port 8000)
docker run -p 8000:8000 --rm serveur-app:latest
```

Avec docker-compose :

```bash
docker-compose up --build
```

Notes:
- L'image installe `iputils-ping` pour fournir la commande `ping` (fallback TCP reste disponible si vous ne souhaitez pas installer ping).
- Le conteneur s'exécute avec un utilisateur non-root `appuser` pour de meilleures pratiques de sécurité.
- Si vous utilisez des scripts qui nécessitent des privilèges réseau avancés (ICMP raw sockets, scapy), vous devrez ajuster les capacités du conteneur (ex: `--cap-add=NET_RAW`) ou exécuter le conteneur en tant que root (non recommandé).