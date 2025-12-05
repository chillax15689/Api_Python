from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import json,os,subprocess,platform,re,ipaddress,datetime,socket
import shutil
import uuid
import io
import csv
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

# Simple background executor and task registry for async scans/actions
executor = ThreadPoolExecutor(max_workers=8)
tasks = {}
from typing import List, Optional
from database import configure_db, engine
from sqlmodel import Session, select
from models.host import Host
from models.action import Action
from models.indicator import Indicator
from models.serveur import Serveur
from models.entreprise import Entreprise
from models.resultats_scans import ScanResult

regip = re.compile(r'^(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}\/([0-9]|[12][0-9]|3[0-2])$')



async def on_start_up():
    configure_db()

app = FastAPI(on_startup=[on_start_up])

@app.get("/hosts")
def read_hosts() -> List[Host]:
    with Session(engine) as session:
        hosts = session.exec(select(Host)).all()
        return hosts
    
@app.get("/host/{host_id}")
def read_host(host_id: int) -> Host:
    with Session(engine) as session:
        host = session.get(Host, host_id)
        if not host: raise HTTPException(status_code=404, detail="Host not found")
        return host
    
@app.post("/host")
def create_host(host: Host) -> Host:
    with Session(engine) as session:
        session.add(host)
        session.commit()
        session.refresh(host)
        return host
    
@app.delete("/host/{host_id}")
def delete_host(host_id: int) -> dict:
    with Session(engine) as session:
        host = session.get(Host, host_id)
        if not host: raise HTTPException(status_code=404, detail="Host not found")
        session.delete(host)
        session.commit()
        return {"ok": True}

@app.put("/host/{host_id}")
def update_host(host_id: int, updated_host: Host) -> Host:
    with Session(engine) as session:
        host = session.get(Host, host_id)
        if not host: raise HTTPException(status_code=404, detail="Host not found")
        host.name = updated_host.name
        host.ip = updated_host.ip
        session.add(host)
        session.commit()
        session.refresh(host)
        return host


@app.get("/actions")
def get_actions() -> List[Action]:
    with Session(engine) as session:
        actions = session.exec(select(Action)).all()
        return actions
    
@app.get("/action/{action_id}")
def get_action(action_id: int) -> Action:
    with Session(engine) as session:
        action = session.get(Action, action_id)
        if not action: raise HTTPException(status_code=404, detail="Action not found")
        return action
    
@app.post("/action")
def create_action(action: Action) -> Action:
    with Session(engine) as session:
        session.add(action)
        session.commit()
        session.refresh(action)
        return action
    
@app.delete("/action/{action_id}")
def delete_action(action_id: int) -> dict:
    with Session(engine) as session:
        action = session.get(Action, action_id)
        if not action: raise HTTPException(status_code=404, detail="Action not found")
        session.delete(action)
        session.commit()
        return {"ok": True}
    
@app.put("/action/{action_id}")
def update_action(action_id: int, updated_action: Action) -> Action:
    with Session(engine) as session:
        action = session.get(Action, action_id)
        if not action: raise HTTPException(status_code=404, detail="Action not found")
        action.name = updated_action.name
        action.script_path = updated_action.script_path
        session.add(action)
        session.commit()
        session.refresh(action)
        return action
    


@app.get("/serveurs")
def read_serveurs() -> List[Serveur]:
    with Session(engine) as session:
        serveurs = session.exec(select(Serveur)).all()
        return serveurs
    
@app.get("/serveurs/{serveur_id}")
def read_serveur(serveur_id: int) -> Serveur:
    with Session(engine) as session:
        serveur = session.get(Serveur, serveur_id)
        if not serveur: 
            raise HTTPException(status_code=404, detail="Serveur not found")
        return serveur
    
@app.post("/serveur")
def create_serveur(serveur: Serveur) -> Serveur:
    with Session(engine) as session:
        session.add(serveur)
        session.commit()
        session.refresh(serveur)
        return serveur
    
@app.delete("/serveur/{serveur_id}")
def delete_serveur(serveur_id: int) -> dict:
    with Session(engine) as session:
        serveur = session.get(Serveur, serveur_id)
        if not serveur: 
            raise HTTPException(status_code=404, detail="Serveur not found")
        session.delete(serveur)
        session.commit()
        return {"ok": True}


@app.get("/entreprises")
def read_entreprises() -> List[Entreprise]:
    with Session(engine) as session:
        entreprises = session.exec(select(Entreprise)).all()
        return entreprises
    
@app.get("/entreprise/{entreprise_id}")
def read_entreprise(entreprise_id: int) -> Entreprise:
    with Session(engine) as session:
        entreprise = session.get(Entreprise, entreprise_id)
        if not entreprise: 
            raise HTTPException(status_code=404, detail="Entreprise not found")
        return entreprise

@app.post("/entreprise")
def create_entreprise(entreprise: Entreprise) -> Entreprise:
    with Session(engine) as session:
        session.add(entreprise)
        session.commit()
        session.refresh(entreprise)
        return entreprise
"""
@app.post("/entreprise")
def create_entreprise(dico: dict) -> Entreprise:
    listehotes = ();listeserveurs = ()
    for i in dico["host"]:
        listehotes.append(read_host(i))
    for i in dico["serveurs"]:
        listeserveurs.append(read_serveur(i))
    entreprise = Entreprise(id=dico["id"],name=dico["name"],serveur=listeserveurs,host=listehotes)
    with Session(engine) as session:
        session.add(entreprise)
        session.commit()
        session.refresh(entreprise)
        return entreprise"""
    
@app.delete("/entreprise/{entreprise_id}")
def delete_entreprise(entreprise_id: int) -> dict:
    with Session(engine) as session:
        entreprise = session.get(Entreprise, entreprise_id)
        if not entreprise: 
            raise HTTPException(status_code=404, detail="Entreprise not found")
        session.delete(entreprise)
        session.commit()
        return {"ok": True}
    
def update_entreprise(entreprise_id: int, updated_entreprise: Entreprise):
    with Session(engine) as session:
        entreprise = session.get(Entreprise, entreprise_id)
        if not entreprise:
            raise HTTPException(status_code=404, detail="Entreprise not found")
        entreprise.name = updated_entreprise.name
        session.commit()
        session.refresh(entreprise)
        return entreprise


def run_cmd(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True, text=True)
        return result.strip()
    except Exception as e:
        return f"Erreur: {e}"
    
@app.get("/mon_pc")
def recup_info():
    os_info = platform.platform()
    system = platform.system()
    if system == "Linux":
        cpu = run_cmd("lscpu | grep 'Model name' || lscpu")
        ram = run_cmd("free -h | grep Mem || free -h")
    elif system == "Windows":
        cpu = run_cmd("wmic cpu get Name")
        ram = run_cmd("wmic computersystem get TotalPhysicalMemory")
    else:
        cpu = "OS non supporté"
        ram = "OS non supporté"

    return {"os": os_info, "cpu": cpu, "ram": ram}

@app.get("/ping/{ip}")
def ping(ip: str):
    reachable = False
    print("1")
    try:
        try:
            response = subprocess.run(ip, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=3)
            reachable = response.returncode == 0
        except subprocess.TimeoutExpired:
            reachable = False
        except FileNotFoundError:
            reachable = False
    except Exception:
        return {"ping impossible": "ping command not found"}
    print("2")
    with Session(engine) as session:
        host = session.exec(select(Host).where(Host.ip == ip)).first()
        host_id = host.id if host else None
        try:
            ports = scan_ports(ip)["open_ports"]
        except Exception:
            ports = []
        scan = ScanResult(host_id=host_id, date=datetime.datetime.now(), open_ports={"ports": ports})
        session.add(scan)
        session.commit()
        session.refresh(scan)
        print("3")
    return {"reachable": reachable, "scan_id": scan.id}

@app.get("/scan/{ip}")
def scan_reseau(ip: str):
    try:
        network = ipaddress.ip_network(ip if "/" in ip else ip + "/24", strict=False)
    except ValueError:
        raise HTTPException(status_code=400, detail="IP réseau non valide")
    results = []
    for host in network.hosts():
        host_ip = str(host)
        results.append({host_ip: ping(host_ip)})
    return {"network": str(network), "results": results}

@app.get("/scan_ports/{ip}")
def scan_ports(ip: str, ports: str = "1-1024"):
    open_ports = []
    try:
        start, end = map(int, ports.split("-"))
    except Exception:
        raise HTTPException(status_code=400, detail="Port range invalide")
    for port in range(start, end + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        try:
            if sock.connect_ex((ip, port)) == 0:
                open_ports.append(port)
        finally:
            sock.close()
    return {"ip": ip, "open_ports": open_ports}

@app.get("/health")
def health_check():
    return {"status": "ok", "time": datetime.datetime.now().isoformat()}


@app.get("/hosts/by_ip/{ip}")
def get_host_by_ip(ip: str):
    with Session(engine) as session:
        host = session.exec(select(Host).where(Host.ip == ip)).first()
        if not host:
            raise HTTPException(status_code=404, detail="Host not found")
        return host


def _run_port_scan_sync(ip: str, ports_range: str):
    return scan_ports(ip, ports_range)


@app.post("/scan_ports_async/{ip}")
def scan_ports_async(ip: str, ports: str = "1-1024"):
    task_id = str(uuid.uuid4())
    future = executor.submit(_run_port_scan_sync, ip, ports)
    tasks[task_id] = {"future": future, "type": "port_scan", "created": time.time(), "meta": {"ip": ip, "ports": ports}}
    return {"task_id": task_id}


@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    info = tasks.get(task_id)
    if not info:
        raise HTTPException(status_code=404, detail="Task not found")
    future = info["future"]
    status = {"task_id": task_id, "type": info.get("type"), "created": info.get("created"), "done": future.done()}
    if future.done():
        try:
            result = future.result()
            status["result"] = result
        except Exception as e:
            status["error"] = str(e)
    return status


@app.get("/scans/recent")
def recent_scans(n: int = 10):
    with Session(engine) as session:
        scans = session.exec(select(ScanResult)).all()
        scans_sorted = sorted(scans, key=lambda s: s.date or datetime.datetime.min, reverse=True)
        return scans_sorted[:n]


@app.get("/stats")
def stats():
    with Session(engine) as session:
        hosts = session.exec(select(Host)).all()
        scans = session.exec(select(ScanResult)).all()
    total_hosts = len(hosts)
    total_scans = len(scans)
    counter = Counter()
    for s in scans:
        try:
            ports = s.open_ports.get("ports") if isinstance(s.open_ports, dict) else s.open_ports
            if isinstance(ports, list):
                counter.update(ports)
            elif isinstance(ports, dict):
                counter.update(ports.keys())
        except Exception:
            continue
    top_ports = counter.most_common(10)
    return {"total_hosts": total_hosts, "total_scans": total_scans, "top_ports": top_ports}


@app.get("/export/scan/{scan_id}")
def export_scan(scan_id: int, format: str = "json"):
    with Session(engine) as session:
        scan = session.get(ScanResult, scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="ScanResult not found")
    if format == "json":
        return scan
    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["scan_id", "host_id", "date", "port"])
        ports = scan.open_ports.get("ports") if isinstance(scan.open_ports, dict) else scan.open_ports
        if isinstance(ports, list):
            for p in ports:
                writer.writerow([scan.id, scan.host_id, scan.date.isoformat() if scan.date else "", p])
        else:
            writer.writerow([scan.id, scan.host_id, scan.date.isoformat() if scan.date else "", ""]) 
        output.seek(0)
        return FileResponse(output, media_type="text/csv")
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")


@app.post("/action/{action_id}/run_on_host/{host_id}")
def run_action_on_host(action_id: int, host_id: int):
    with Session(engine) as session:
        action = session.get(Action, action_id)
        host = session.get(Host, host_id)
        if not action or not host:
            raise HTTPException(status_code=404, detail="Action or Host not found")
    if not getattr(action, "script_path", None):
        raise HTTPException(status_code=400, detail="Action has no script_path configured")
    def _run_action(script, target_ip):
        try:
            proc = subprocess.run([script, target_ip], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)
            return {"returncode": proc.returncode, "output": proc.stdout}
        except Exception as e:
            return {"error": str(e)}
    task_id = str(uuid.uuid4())
    future = executor.submit(_run_action, action.script_path, host.ip)
    tasks[task_id] = {"future": future, "type": "action_run", "created": time.time(), "meta": {"action_id": action_id, "host_id": host_id}}
    return {"task_id": task_id}

@app.get("/dns/{domain}")
def dns_lookup(domain: str):
    try:
        ip = socket.gethostbyname(domain)
        return {"domain": domain, "ip": ip}
    except:
        raise HTTPException(400, "Domain could not be resolved")

@app.get("/scans/{scan_id}")
def read_scans(scan_id: int):
    with Session(engine) as session:
        scan = session.get(ScanResult, scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="ScanResult not found")
        return scan

@app.get("/host/{host_id}/indicators")
def get_host_indicators(host_id: int) -> List[Indicator]:
    with Session(engine) as session:
        indicators = session.exec(select(Indicator).where(Indicator.host_id == host_id)).all()
        return indicators
    
@app.post("/host/{host_id}/indicator")
def create_host_indicator(host_id: int, indicator: Indicator) -> Indicator:
    with Session(engine) as session:
        indicator.host_id = host_id
        session.add(indicator)
        session.commit()
        session.refresh(indicator)
        return indicator
    
@app.delete("/indicator/{indicator_id}")
def delete_indicator(indicator_id: int) -> dict:
    with Session(engine) as session:
        indicator = session.get(Indicator, indicator_id)
        if not indicator:
            raise HTTPException(status_code=404, detail="Indicator not found")
        session.delete(indicator)
        session.commit()
        return {"ok": True}


@app.delete("/host/{host_id}/indicator/{indicator_id}")
def delete_host_indicator(host_id: int, indicator_id: int) -> dict:
    with Session(engine) as session:
        indicator = session.get(Indicator, indicator_id)
        if not indicator or indicator.host_id != host_id:
            raise HTTPException(status_code=404, detail="Indicator not found")
        session.delete(indicator)
        session.commit()
        return {"ok": True}