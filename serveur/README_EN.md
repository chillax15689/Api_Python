# Serveur API

This repository provides a FastAPI-based API to manage network resources (hosts, servers, companies), execute configured actions, and collect scan results (port scans, reachability). The main application file is `main.py`.

## Table of Contents

- Installation
- Running the service
- Architecture and components
- Main endpoints
- Background tasks
- Export and statistics
- Limitations and recommendations
- Troubleshooting


## Installation

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you don't have a complete `requirements.txt`, install at least:

```bash
pip install fastapi uvicorn sqlmodel sqlalchemy pydantic
```

Note for containers: if you rely on the system `ping` command, install it in the image (Debian/Ubuntu):

```bash
apt-get update && apt-get install -y iputils-ping
```


## Running

Start the server in development mode:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000` by default.


## Architecture and components

- `main.py`: FastAPI application and endpoints. Contains:
  - CRUD endpoints for `Host`, `Action`, `Indicator`, `Serveur`, `Entreprise`.
  - Network operations (`ping`, `scan_ports`, `scan_reseau`) and persistence of `ScanResult`.
  - Background task support via a `ThreadPoolExecutor` and a simple `tasks` registry.
- `database.py`: database configuration (engine, session creation).
- `models/`: SQLModel model definitions (`Host`, `Action`, `Indicator`, `Serveur`, `Entreprise`, `ScanResult`).


## Main endpoints (summary)

- GET /health
  - Simple health check.

- Hosts
  - GET /hosts — list hosts.
  - GET /host/{host_id} — get a host.
  - POST /host — create a host (body = Host model).
  - PUT /host/{host_id} — update a host.
  - DELETE /host/{host_id} — delete a host.
  - GET /hosts/by_ip/{ip} — convenience lookup by IP.

- Actions
  - GET /actions
  - GET /action/{action_id}
  - POST /action
  - PUT /action/{action_id}
  - DELETE /action/{action_id}
  - POST /action/{action_id}/run_on_host/{host_id} — schedule execution of `Action.script_path` on the target host (returns a `task_id`).

- Companies / Servers
  - Standard CRUD endpoints for companies and servers (see `main.py`).

- Indicators
  - GET /host/{host_id}/indicators
  - POST /host/{host_id}/indicator
  - DELETE /indicator/{indicator_id}
  - DELETE /host/{host_id}/indicator/{indicator_id}

- Scans & Network
  - GET /ping/{ip} — tries system `ping`, falls back to simple TCP connect attempts (ports 80/443/22). Stores a `ScanResult`.
  - GET /scan/{ip} — network scan by CIDR or IP (defaults to /24 for bare IP); iterates hosts and calls `ping` for each.
  - GET /scan_ports/{ip}?ports=1-1024 — synchronous port scan.
  - POST /scan_ports_async/{ip} — schedules a background port scan, returns `task_id`.
  - GET /scans/{scan_id} — retrieve a `ScanResult`.
  - GET /scans/recent?n=10 — list most recent scans.

- Tasks and export
  - GET /tasks/{task_id} — check background task status/result.
  - GET /stats — basic statistics (total hosts, total scans, top observed open ports).
  - GET /export/scan/{scan_id}?format=json|csv — export a scan as JSON or CSV. CSV yields one row per open port.


## Model formats (reminder)

- ScanResult
  - id : int
  - host_id : Optional[int]
  - date : datetime
  - open_ports : JSON/dict

- Host, Action, Indicator, Serveur, Entreprise
  - See the `models/` folder for exact SQLModel classes.


## Usage examples

- Start an asynchronous port scan:

```bash
curl -X POST http://127.0.0.1:8000/scan_ports_async/192.0.2.10
# returns: {"task_id":"..."}

curl http://127.0.0.1:8000/tasks/<task_id>
```

- Export a scan as CSV:

```bash
curl -OJ "http://127.0.0.1:8000/export/scan/12?format=csv"
```

- Run an Action script on a Host (executes `Action.script_path` with the host IP as argument):

```bash
curl -X POST http://127.0.0.1:8000/action/5/run_on_host/3
# returns: {"task_id":"..."}
```


## Limitations, security and performance

1. Network permissions
   - Using ICMP (`ping`) or raw sockets (scapy) may require root privileges. For container environments, install `iputils-ping` or give NET_RAW capability if using raw sockets.

2. Performance
   - `scan_reseau` and `scan_ports` are synchronous by default and can be slow for large ranges. Use the asynchronous port-scan endpoint to avoid blocking the API.
   - `scan_reseau` creates one `ScanResult` per host scanned; be mindful of DB growth.

3. Security
   - Executing external scripts via `Action.script_path` is potentially dangerous. Validate and authorize actions properly; add authentication/authorization to restrict access.

4. Concurrency and resource limits
   - The default `ThreadPoolExecutor` has limited workers; monitor file descriptor and socket usage if many scans/actions run concurrently.


## Troubleshooting

- `FileNotFoundError: [Errno 2] No such file or directory: 'ping'` — install `iputils-ping` in the OS image or rely on the TCP fallback.
- `ModuleNotFoundError: No module named 'fastapi'` — install the project dependencies with `pip install -r requirements.txt`.
- ICMP permission issues — run with elevated privileges or grant NET_RAW capability to the container.


## Docker

A `Dockerfile` and a `docker-compose.yml` have been added to run the application in a container.

Build and run with Docker:

```bash
# build the image
docker build -t serveur-app:latest .

# run (exposes port 8000)
docker run -p 8000:8000 --rm serveur-app:latest
```

With docker-compose:

```bash
docker-compose up --build
```

Notes:
- The image installs `iputils-ping` to provide the `ping` command (the TCP fallback remains available if you prefer not to rely on ping).
- The container runs as a non-root user `appuser` for better security practices.
- If your action scripts require advanced network privileges (raw ICMP sockets, scapy), you will need to adjust container capabilities (e.g., `--cap-add=NET_RAW`) or run as root (not recommended).

Tell me which follow-up you'd like.