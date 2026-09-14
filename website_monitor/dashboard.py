import subprocess
import os
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
processes = {}

SCRIPTS = {
    "website_monitor": "website_monitor.py",
    "price_api": "price_api.py",
    "check_url_api": "check_url_api.py",
    "fast_rakuten_scanner": "fast_rakuten_scanner.py"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    status = {}
    for name in SCRIPTS:
        proc = processes.get(name)
        # Check if process exists and is still running (poll() returns None if running)
        if proc and proc.poll() is None:
            status[name] = "running"
        else:
            status[name] = "stopped"
    return jsonify(status)

@app.route('/api/start/<script_name>', methods=['POST'])
def start_script(script_name):
    if script_name not in SCRIPTS:
        return jsonify({"error": "Script không tồn tại"}), 404
        
    proc = processes.get(script_name)
    if proc and proc.poll() is None:
        return jsonify({"message": "Đã đang chạy rồi"}), 200
        
    script_path = SCRIPTS[script_name]
    # Khởi chạy Process mới (sử dụng 'py' trên Windows)
    p = subprocess.Popen(["py", script_path], cwd=os.path.dirname(os.path.abspath(__file__)))
    processes[script_name] = p
    
    return jsonify({"message": "Khởi động thành công!"})

@app.route('/api/stop/<script_name>', methods=['POST'])
def stop_script(script_name):
    proc = processes.get(script_name)
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        return jsonify({"message": "Đã dừng script thành công"})
    return jsonify({"message": "Script đang không chạy"})

if __name__ == '__main__':
    print("Dashboard Control Center đang chạy tại http://127.0.0.1:8080")
    app.run(host='127.0.0.1', port=8080)
