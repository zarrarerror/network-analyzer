from flask import Flask, request, render_template_string, Response, redirect, url_for, send_file
import subprocess
import threading
import os

app = Flask(__name__)
live_capture_process = None
captured_data = []
FILTER_OPTIONS = ["IP", "Source IP", "Destination IP", "TCP", "UDP"]

# HTML Template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Network Analyzer</title>
    <style>
        body { background-color: #121212; color: #f5f5f5; font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: #4caf50; }
        select, input[type=text], button { background-color: #2b2b2b; color: white; border: 1px solid #4caf50; padding: 10px; margin: 5px; width: 250px; }
        pre { background-color: #2b2b2b; padding: 10px; white-space: pre-wrap; overflow-x: auto; height: 400px; overflow-y: scroll; }
        .capture-buttons { margin: 10px 0; }
    </style>
    <script>
        function refreshOutput() {
            fetch('/live-data')
                .then(response => response.text())
                .then(data => document.getElementById('output').innerText = data);
        }
        setInterval(refreshOutput, 2000);
        
        function suggestCommands() {
            const input = document.getElementById('customCommand').value;
            const suggestions = document.getElementById('suggestions');
            suggestions.innerHTML = '';
            const commands = ["tcpdump -i any", "tcpdump port 80", "tcpdump udp", "tcpdump -c 10"]; // Add more common commands
            commands.filter(cmd => cmd.includes(input)).forEach(s => {
                const div = document.createElement('div');
                div.innerText = s;
                div.onclick = () => { document.getElementById('customCommand').value = s; };
                suggestions.appendChild(div);
            });
        }
    </script>
</head>
<body>
    <h1>Network Traffic Analyzer</h1>
    
    <div class="capture-buttons">
        <button onclick="location.href='/live-capture/start'">Start Capture</button>
        <button onclick="location.href='/live-capture/stop'">Stop Capture</button>
        <button onclick="location.href='/export/txt'">Export to .txt</button>
        <button onclick="location.href='/export/cap'">Export to .cap</button>
    </div>
    
    <div class="filter-form">
        <form method="post" action="/filter">
            <label for="filter">Apply Filter:</label>
            <select name="filter_type">
                {% for option in filters %}
                    <option value="{{ option }}">{{ option }}</option>
                {% endfor %}
            </select>
            <input type="text" name="filter_value" placeholder="Enter filter criteria">
            <input type="submit" value="Apply Filter">
        </form>
    </div>

    <h2>Live Capture Output:</h2>
    <pre id="output">{{ output }}</pre>

    <h2>Custom Command:</h2>
    <input type="text" id="customCommand" onkeyup="suggestCommands()" placeholder="Enter custom tcpdump command">
    <button onclick="location.href='/custom-command?cmd=' + document.getElementById('customCommand').value">Run Custom Command</button>
    <div id="suggestions" style="background-color: #333; padding: 10px;"></div>
</body>
</html>
"""

# Function to capture packets
def capture_packets():
    global live_capture_process, captured_data
    captured_data.clear()
    live_capture_process = subprocess.Popen(
        ["tcpdump", "-l", "-n"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    for line in iter(live_capture_process.stdout.readline, ''):
        captured_data.append(line.strip())
        if len(captured_data) > 100:
            captured_data.pop(0)

@app.route("/live-capture/start")
def live_capture_start():
    global live_capture_process
    if not live_capture_process or live_capture_process.poll() is not None:
        threading.Thread(target=capture_packets, daemon=True).start()
    return redirect(url_for("index"))

@app.route("/live-capture/stop")
def live_capture_stop():
    global live_capture_process
    if live_capture_process:
        live_capture_process.terminate()
        live_capture_process = None
    return redirect(url_for("index"))

@app.route("/live-data")
def live_data():
    return "\n".join(captured_data[-50:])

@app.route("/export/<file_type>")
def export_data(file_type):
    global captured_data
    filename = f"capture.{file_type}"
    if file_type == "txt":
        with open(filename, "w") as file:
            file.write("\n".join(captured_data))
    elif file_type == "cap":
        subprocess.run(["tcpdump", "-w", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return send_file(filename, as_attachment=True)

@app.route("/custom-command")
def run_custom_command():
    custom_cmd = request.args.get("cmd")
    output = subprocess.run(custom_cmd, shell=True, capture_output=True, text=True).stdout
    captured_data.extend(output.split("\n"))
    return redirect(url_for("index"))

@app.route("/", methods=["GET"])
def index():
    return render_template_string(html_template, output="\n".join(captured_data[-50:]), filters=FILTER_OPTIONS)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
