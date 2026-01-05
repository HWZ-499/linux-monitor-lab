from collections import deque
from datetime import datetime, timezone
from flask import Flask, jsonify, render_template
from pathlib import Path
import subprocess

app = Flask(__name__)

# scripts 目录：backend 的上一级的 scripts
SCRIPTS_DIR = (Path(__file__).resolve().parent.parent / "scripts").resolve()
REFRESH_SECONDS = 5
ALERT_THRESHOLDS = {
    "cpu": 90.0,
    "mem": 90.0,
    "disk": 90.0,
}
HISTORY_MAX = 60
HISTORY = deque(maxlen=HISTORY_MAX)

def run_script(script_name: str, *args: str) -> str:
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return f"ERROR: {script_name} not found at {script_path}"

    try:
        # 运行脚本，拿到输出文本
        out = subprocess.check_output(
            ["/bin/bash", str(script_path), *args],
            stderr=subprocess.STDOUT,
            timeout=5,
            text=True
        )
        return out.strip()
    except subprocess.CalledProcessError as e:
        return f"ERROR running {script_name}:\n{e.output}"
    except subprocess.TimeoutExpired:
        return f"ERROR: {script_name} timed out"

def parse_percentage(value: str) -> float | None:
    try:
        return float(value.strip().rstrip("%"))
    except ValueError:
        return None

def parse_cpu_output(output: str) -> dict:
    if output.startswith("ERROR"):
        return {"ok": False, "error": output}
    usage = None
    for line in output.splitlines():
        if line.startswith("CPU Usage:"):
            usage = parse_percentage(line.split(":", 1)[1])
            break
    return {
        "ok": usage is not None,
        "usage": usage,
        "alert": usage is not None and usage >= ALERT_THRESHOLDS["cpu"],
        "text": output,
    }

def parse_mem_output(output: str) -> dict:
    if output.startswith("ERROR"):
        return {"ok": False, "error": output}
    data = {"total_mb": None, "used_mb": None, "avail_mb": None, "usage": None}
    for line in output.splitlines():
        if line.startswith("Total:"):
            data["total_mb"] = parse_percentage(line.split(":", 1)[1].strip().replace(" MB", ""))
        elif line.startswith("Used"):
            data["used_mb"] = parse_percentage(line.split(":", 1)[1].strip().replace(" MB", ""))
        elif line.startswith("Avail"):
            data["avail_mb"] = parse_percentage(line.split(":", 1)[1].strip().replace(" MB", ""))
        elif line.startswith("Usage:"):
            data["usage"] = parse_percentage(line.split(":", 1)[1])
    usage = data["usage"]
    return {
        "ok": usage is not None,
        **data,
        "alert": usage is not None and usage >= ALERT_THRESHOLDS["mem"],
        "text": output,
    }

def parse_disk_output(output: str) -> dict:
    if output.startswith("ERROR"):
        return {"ok": False, "error": output}
    data = {"total": None, "used": None, "avail": None, "usage": None}
    for line in output.splitlines():
        if line.startswith("Total:"):
            data["total"] = line.split(":", 1)[1].strip()
        elif line.startswith("Used"):
            data["used"] = line.split(":", 1)[1].strip()
        elif line.startswith("Avail"):
            data["avail"] = line.split(":", 1)[1].strip()
        elif line.startswith("Usage:"):
            data["usage"] = parse_percentage(line.split(":", 1)[1])
    usage = data["usage"]
    return {
        "ok": usage is not None,
        **data,
        "alert": usage is not None and usage >= ALERT_THRESHOLDS["disk"],
        "text": output,
    }

def parse_process_lines(lines: list[str]) -> list[dict]:
    items = []
    for line in lines:
        if not line.strip() or line.strip().startswith("PID"):
            continue
        parts = line.split(None, 3)
        if len(parts) < 4:
            continue
        pid, command, cpu, mem = parts
        items.append({
            "pid": int(pid),
            "command": command,
            "cpu": parse_percentage(cpu),
            "mem": parse_percentage(mem),
        })
    return items

def parse_proc_output(output: str) -> dict:
    if output.startswith("ERROR"):
        return {"ok": False, "error": output}
    lines = output.splitlines()
    cpu_lines = []
    mem_lines = []
    current = None
    for line in lines:
        if line.strip() == "[Top 5 by CPU]":
            current = cpu_lines
            continue
        if line.strip() == "[Top 5 by MEM]":
            current = mem_lines
            continue
        if current is not None:
            current.append(line)
    return {
        "ok": True,
        "top_cpu": parse_process_lines(cpu_lines),
        "top_mem": parse_process_lines(mem_lines),
        "text": output,
    }

def parse_process_detail(output: str) -> dict:
    if output.startswith("ERROR"):
        return {"ok": False, "error": output}
    detail = {"ok": True}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        detail_key = key.strip().lower().replace(" ", "_")
        detail[detail_key] = value.strip()
    return detail

def add_history(status: dict) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    HISTORY.append({
        "timestamp": timestamp,
        "cpu": status.get("cpu", {}).get("usage"),
        "mem": status.get("mem", {}).get("usage"),
        "disk": status.get("disk", {}).get("usage"),
    })

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/config")
def api_config():
    return jsonify({
        "refreshSeconds": REFRESH_SECONDS,
        "thresholds": ALERT_THRESHOLDS,
        "historyMax": HISTORY_MAX,
    })

@app.route("/api/status")
def api_status():
    status = {
        "cpu": parse_cpu_output(run_script("cpu_monitor.sh")),
        "mem": parse_mem_output(run_script("mem_monitor.sh")),
        "disk": parse_disk_output(run_script("disk_monitor.sh")),
        "proc": parse_proc_output(run_script("process_monitor.sh")),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    add_history(status)
    return jsonify(status)

@app.route("/api/history")
def api_history():
    return jsonify({
        "items": list(HISTORY),
    })

@app.route("/api/process/<int:pid>")
def api_process_detail(pid: int):
    output = run_script("process_detail.sh", str(pid))
    return jsonify(parse_process_detail(output))

if __name__ == "__main__":
    # Kali 下用开发模式够用
    app.run(host="0.0.0.0", port=5000)
