from flask import Flask, jsonify, render_template
import subprocess
from pathlib import Path

app = Flask(__name__)

# scripts 目录：backend 的上一级的 scripts
SCRIPTS_DIR = (Path(__file__).resolve().parent.parent / "scripts").resolve()

def run_script(script_name: str) -> str:
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return f"ERROR: {script_name} not found at {script_path}"

    try:
        # 运行脚本，拿到输出文本
        out = subprocess.check_output(
            ["/bin/bash", str(script_path)],
            stderr=subprocess.STDOUT,
            timeout=5,
            text=True
        )
        return out.strip()
    except subprocess.CalledProcessError as e:
        return f"ERROR running {script_name}:\n{e.output}"
    except subprocess.TimeoutExpired:
        return f"ERROR: {script_name} timed out"

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/status")
def api_status():
    data = {
        "cpu": run_script("cpu_monitor.sh"),
        "mem": run_script("mem_monitor.sh"),
        "disk": run_script("disk_monitor.sh"),
        "proc": run_script("process_monitor.sh"),
    }
    return jsonify(data)

if __name__ == "__main__":
    # Kali 下用开发模式够用
    app.run(host="0.0.0.0", port=5000)

