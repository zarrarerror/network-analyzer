from flask import Flask, request, render_template_string, send_file, jsonify
import subprocess
import os

app = Flask(__name__)

EXPORT_FILE_PATH = "exported_data.txt"

# Common tcpdump commands with explanations
COMMAND_LIBRARY = {
    "sudo tcpdump -c 10": "Capture 10 packets from the default interface.",
    "sudo tcpdump -i any -c 5": "Capture 5 packets from any available interface.",
    "sudo tcpdump -i eth0 -c 10": "Capture 10 packets from the eth0 interface.",
    "sudo tcpdump -i eth0 port 80 -c 5": "Capture 5 HTTP packets on eth0 (port 80).",
    "sudo tcpdump -i eth0 udp -c 5": "Capture 5 UDP packets on eth0.",
    "sudo tcpdump -nn -i eth0": "Capture packets without resolving names (-nn) on eth0.",
    "sudo tcpdump -A": "Print packet contents in ASCII format.",
    "sudo tcpdump -XX": "Capture packets with link-level headers and data in hex and ASCII.",
    "sudo tcpdump -w file.pcap": "Write packet data to file.pcap for later analysis.",
}

html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Analyzer</title>
    <style>
        body { background-color: #121212; color: #f5f5f5; font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: #4caf50; }
        form { margin-bottom: 20px; }
        select, input[type=text], input[type=submit] { background-color: #2b2b2b; color: white; border: 1px solid #4caf50; padding: 10px; margin: 5px 0; width: 100%; }
        input[type=submit] { cursor: pointer; }
        pre { background-color: #2b2b2b; padding: 10px; white-space: pre-wrap; overflow-x: auto; }
        a { color: #4caf50; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .suggestions { background-color: #2b2b2b; border: 1px solid #4caf50; max-height: 150px; overflow-y: auto; }
        .suggestions div { padding: 5px; cursor: pointer; }
        .suggestions div:hover { background-color: #4caf50; color: white; }
        .command-library { margin-top: 20px; }
        .command-library h2 { color: #4caf50; }
        .command-library ul { list-style-type: none; padding: 0; }
        .command-library li { margin: 10px 0; }
    </style>
    <script>
        function showSuggestions(input) {
            const suggestions = document.getElementById("suggestions");
            const commands = {{ command_keys | tojson }};
            suggestions.innerHTML = "";
            if (!input) return;
            const filtered = commands.filter(cmd => cmd.includes(input));
            filtered.forEach(cmd => {
                const div = document.createElement("div");
                div.textContent = cmd;
                div.onclick = () => document.getElementById("custom_command").value = cmd;
                suggestions.appendChild(div);
            });
        }
    </script>
</head>
<body>
    <h1>Network Traffic Analyzer</h1>
    <form method="post">
        <label for="command">Select Command:</label>
        <select name="command">
            {% for cmd, desc in command_library.items() %}
                <option value="{{ cmd }}">{{ desc }}</option>
            {% endfor %}
        </select><br><br>
        <label for="custom_command">Or Enter Custom Command:</label>
        <input type="text" id="custom_command" name="custom_command" oninput="showSuggestions(this.value)" placeholder="Enter custom tcpdump command"><br>
        <div id="suggestions" class="suggestions"></div><br>
        <input type="submit" value="Run Command">
    </form>
    <h2>Output:</h2>
    <pre>{{output}}</pre>
    {% if output %}
    <a href="/export" target="_blank">Export Data as .txt</a>
    {% endif %}
    <div class="command-library">
        <h2>Command Library</h2>
        <ul>
            {% for cmd, desc in command_library.items() %}
                <li><strong>{{ cmd }}</strong>: {{ desc }}</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
        command = request.form.get("command") or request.form.get("custom_command")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                output = result.stdout
                with open(EXPORT_FILE_PATH, "w") as file:
                    file.write(output)
            else:
                output = f"Error:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            output = "Error: Command timed out. Try reducing the packet count."
        except Exception as e:
            output = f"Error:\n{str(e)}"
    return render_template_string(html_template, output=output, command_library=COMMAND_LIBRARY, command_keys=list(COMMAND_LIBRARY.keys()))

@app.route("/export")
def export():
    if os.path.exists(EXPORT_FILE_PATH):
        return send_file(EXPORT_FILE_PATH, as_attachment=True)
    return "Error: No data available to export."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
