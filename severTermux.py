#!/usr/bin/env python3
import http.server
import socketserver
import os
import subprocess
import json
import cgi
import threading
import time
import psutil
import platform
from pathlib import Path
import datetime

class WebShellHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.send_html_interface()
        elif self.path == '/api/files':
            self.list_files()
        elif self.path.startswith('/api/file/'):
            self.get_file_content()
        elif self.path == '/api/status':
            self.get_system_status()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/run':
            self.run_command()
        elif self.path == '/api/file':
            self.create_file()
        elif self.path == '/api/upload':
            self.upload_file()
        elif self.path == '/api/delete':
            self.delete_file()
        elif self.path == '/api/ping':
            self.test_ping()
        else:
            self.send_error(404)
    
    def send_html_interface(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Termux Web Shell</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { 
                    font-family: 'Courier New', monospace; 
                    background: #1e1e1e; 
                    color: #00ff00; 
                    padding: 20px;
                    line-height: 1.6;
                }
                .container { max-width: 100%; }
                .header { text-align: center; margin-bottom: 20px; padding: 10px; border-bottom: 1px solid #00ff00; }
                .panels { display: flex; flex-direction: column; gap: 20px; }
                @media (min-width: 768px) { .panels { flex-direction: row; } }
                .panel { flex: 1; background: #2d2d2d; padding: 15px; border-radius: 5px; border: 1px solid #444; }
                .panel h3 { margin-bottom: 10px; color: #00ff00; }
                textarea, input, select, button { 
                    width: 100%; 
                    padding: 10px; 
                    margin: 5px 0; 
                    background: #1a1a1a; 
                    color: #00ff00; 
                    border: 1px solid #444; 
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }
                button { 
                    background: #006600; 
                    color: white; 
                    border: none; 
                    cursor: pointer;
                    transition: background 0.3s;
                }
                button:hover { background: #008800; }
                .output { 
                    background: #000; 
                    color: #00ff00; 
                    padding: 10px; 
                    border-radius: 3px; 
                    min-height: 200px; 
                    max-height: 400px; 
                    overflow-y: auto;
                    white-space: pre-wrap;
                    font-family: 'Courier New', monospace;
                }
                .file-item { 
                    padding: 5px; 
                    border-bottom: 1px solid #444; 
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                }
                .file-item:hover { background: #3d3d3d; }
                .file-actions button { 
                    width: auto; 
                    padding: 2px 8px; 
                    margin-left: 5px; 
                    font-size: 12px;
                }
                .success { color: #00ff00; }
                .error { color: #ff0000; }
                .warning { color: #ffff00; }
                .info { color: #00ffff; }
                
                /* Status Panel Styles */
                .status-panel { 
                    background: linear-gradient(135deg, #2d2d2d, #1a1a1a);
                    border: 1px solid #00ff00;
                }
                .status-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 10px;
                    margin-top: 10px;
                }
                .status-item {
                    background: #1a1a1a;
                    padding: 10px;
                    border-radius: 5px;
                    border-left: 4px solid #00ff00;
                }
                .status-label {
                    font-size: 12px;
                    color: #888;
                    margin-bottom: 5px;
                }
                .status-value {
                    font-size: 14px;
                    font-weight: bold;
                }
                .progress-bar {
                    width: 100%;
                    height: 8px;
                    background: #333;
                    border-radius: 4px;
                    margin-top: 5px;
                    overflow: hidden;
                }
                .progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #00ff00, #00cc00);
                    transition: width 0.3s ease;
                }
                .cpu-usage { background: linear-gradient(90deg, #ff6b6b, #ee5a24); }
                .ram-usage { background: linear-gradient(90deg, #00ff00, #00cc00); }
                .disk-usage { background: linear-gradient(90deg, #00ffff, #0099cc); }
                
                .refresh-btn {
                    background: #0088cc;
                    padding: 5px 10px;
                    font-size: 12px;
                    margin-top: 10px;
                }
                .refresh-btn:hover { background: #00aaff; }
                
                .ping-test {
                    background: #006600;
                    padding: 5px 10px;
                    font-size: 12px;
                    margin-top: 5px;
                }
                .ping-test:hover { background: #008800; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Termux Web Shell Server</h1>
                    <p>Current Directory: <span id="currentDir"></span></p>
                    <p>Server Time: <span id="serverTime"></span></p>
                </div>
                
                <div class="panels">
                    <!-- Status Panel -->
                    <div class="panel status-panel">
                        <h3>📊 System Status</h3>
                        <div id="statusContent">
                            <div class="status-grid">
                                <div class="status-item">
                                    <div class="status-label">🖥️ CPU Usage</div>
                                    <div class="status-value" id="cpuUsage">Loading...</div>
                                    <div class="progress-bar"><div class="progress-fill cpu-usage" id="cpuBar" style="width: 0%"></div></div>
                                </div>
                                <div class="status-item">
                                    <div class="status-label">💾 RAM Usage</div>
                                    <div class="status-value" id="ramUsage">Loading...</div>
                                    <div class="progress-bar"><div class="progress-fill ram-usage" id="ramBar" style="width: 0%"></div></div>
                                </div>
                                <div class="status-item">
                                    <div class="status-label">💽 Disk Usage</div>
                                    <div class="status-value" id="diskUsage">Loading...</div>
                                    <div class="progress-bar"><div class="progress-fill disk-usage" id="diskBar" style="width: 0%"></div></div>
                                </div>
                                <div class="status-item">
                                    <div class="status-label">🌐 Network Ping</div>
                                    <div class="status-value" id="pingStatus">Click to test</div>
                                    <button class="ping-test" onclick="testPing()">Test Ping Google</button>
                                </div>
                                <div class="status-item">
                                    <div class="status-label">⏰ Uptime</div>
                                    <div class="status-value" id="uptime">Loading...</div>
                                </div>
                                <div class="status-item">
                                    <div class="status-label">📱 Platform</div>
                                    <div class="status-value" id="platform">Loading...</div>
                                </div>
                                <div class="status-item">
                                    <div class="status-label">🔥 Processes</div>
                                    <div class="status-value" id="processCount">Loading...</div>
                                </div>
                                <div class="status-item">
                                    <div class="status-label">🌡️ CPU Cores</div>
                                    <div class="status-value" id="cpuCores">Loading...</div>
                                </div>
                            </div>
                            <button class="refresh-btn" onclick="refreshStatus()">🔄 Refresh Status</button>
                        </div>
                    </div>
                </div>

                <div class="panels">
                    <!-- Command Panel -->
                    <div class="panel">
                        <h3>🔧 Execute Command</h3>
                        <select id="commandType">
                            <option value="shell">Shell Command</option>
                            <option value="python">Python Script</option>
                            <option value="node">Node.js</option>
                            <option value="php">PHP</option>
                            <option value="bash">Bash Script</option>
                        </select>
                        <textarea id="command" placeholder="Enter command or code..." rows="5"></textarea>
                        <button onclick="runCommand()">▶ Run</button>
                        <div class="output" id="output"></div>
                    </div>

                    <!-- File Manager -->
                    <div class="panel">
                        <h3>📁 File Manager</h3>
                        <div>
                            <input type="text" id="filename" placeholder="File name">
                            <textarea id="filecontent" placeholder="File content..." rows="5"></textarea>
                            <button onclick="createFile()">Create File</button>
                            <input type="file" id="fileUpload" style="margin: 10px 0;">
                            <button onclick="uploadFile()">Upload File</button>
                        </div>
                        <div id="fileList" style="margin-top: 10px;"></div>
                    </div>
                </div>
            </div>

            <script>
                let currentFile = '';
                let statusInterval;
                
                // Load initial data
                document.addEventListener('DOMContentLoaded', function() {
                    loadFiles();
                    getCurrentDir();
                    refreshStatus();
                    updateServerTime();
                    
                    // Auto refresh status every 5 seconds
                    statusInterval = setInterval(refreshStatus, 5000);
                    setInterval(updateServerTime, 1000);
                });

                function updateServerTime() {
                    const now = new Date();
                    document.getElementById('serverTime').textContent = now.toLocaleString();
                }

                function getCurrentDir() {
                    fetch('/api/run', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command: 'pwd' })
                    })
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('currentDir').textContent = data.output;
                    });
                }

                function refreshStatus() {
                    fetch('/api/status')
                        .then(response => response.json())
                        .then(data => {
                            // CPU
                            document.getElementById('cpuUsage').textContent = `${data.cpu_usage}%`;
                            document.getElementById('cpuBar').style.width = `${data.cpu_usage}%`;
                            
                            // RAM
                            const ramUsedGB = (data.ram_used / 1024 / 1024 / 1024).toFixed(2);
                            const ramTotalGB = (data.ram_total / 1024 / 1024 / 1024).toFixed(2);
                            const ramPercent = data.ram_percent;
                            document.getElementById('ramUsage').textContent = `${ramUsedGB}GB / ${ramTotalGB}GB (${ramPercent}%)`;
                            document.getElementById('ramBar').style.width = `${ramPercent}%`;
                            
                            // Disk
                            const diskUsedGB = (data.disk_used / 1024 / 1024 / 1024).toFixed(2);
                            const diskTotalGB = (data.disk_total / 1024 / 1024 / 1024).toFixed(2);
                            const diskPercent = data.disk_percent;
                            document.getElementById('diskUsage').textContent = `${diskUsedGB}GB / ${diskTotalGB}GB (${diskPercent}%)`;
                            document.getElementById('diskBar').style.width = `${diskPercent}%`;
                            
                            // Other info
                            document.getElementById('uptime').textContent = data.uptime;
                            document.getElementById('platform').textContent = data.platform;
                            document.getElementById('processCount').textContent = data.process_count;
                            document.getElementById('cpuCores').textContent = data.cpu_cores;
                        })
                        .catch(error => {
                            console.error('Status update failed:', error);
                        });
                }

                function testPing() {
                    const pingElement = document.getElementById('pingStatus');
                    pingElement.innerHTML = '⏳ Testing ping...';
                    
                    fetch('/api/ping', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ host: 'google.com' })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            pingElement.innerHTML = `✅ ${data.ping_time}`;
                        } else {
                            pingElement.innerHTML = `❌ Failed: ${data.error}`;
                        }
                    })
                    .catch(error => {
                        pingElement.innerHTML = `❌ Error: ${error}`;
                    });
                }

                function runCommand() {
                    const commandType = document.getElementById('commandType').value;
                    const command = document.getElementById('command').value;
                    const output = document.getElementById('output');
                    
                    output.innerHTML = '⏳ Running...';
                    
                    let finalCommand = command;
                    switch(commandType) {
                        case 'python':
                            finalCommand = `python3 -c "${command.replace(/"/g, '\\"')}"`;
                            break;
                        case 'node':
                            finalCommand = `node -e "${command.replace(/"/g, '\\"')}"`;
                            break;
                        case 'php':
                            finalCommand = `php -r "${command.replace(/"/g, '\\"')}"`;
                            break;
                        case 'bash':
                            finalCommand = `bash -c "${command.replace(/"/g, '\\"')}"`;
                            break;
                    }
                    
                    fetch('/api/run', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command: finalCommand })
                    })
                    .then(response => response.json())
                    .then(data => {
                        output.innerHTML = `<span class="success">✓ Command executed successfully</span>\n\n${data.output}`;
                        if (data.error) {
                            output.innerHTML += `\n\n<span class="error">✗ Error:</span>\n${data.error}`;
                        }
                        loadFiles(); // Refresh file list
                        refreshStatus(); // Refresh status
                    })
                    .catch(error => {
                        output.innerHTML = `<span class="error">✗ Request failed: ${error}</span>`;
                    });
                }

                function loadFiles() {
                    fetch('/api/files')
                        .then(response => response.json())
                        .then(files => {
                            const fileList = document.getElementById('fileList');
                            fileList.innerHTML = '<h4>Files in current directory:</h4>';
                            
                            files.forEach(file => {
                                const fileItem = document.createElement('div');
                                fileItem.className = 'file-item';
                                fileItem.innerHTML = `
                                    <span onclick="viewFile('${file}')">📄 ${file}</span>
                                    <div class="file-actions">
                                        <button onclick="runFile('${file}')">Run</button>
                                        <button onclick="deleteFile('${file}')">Delete</button>
                                    </div>
                                `;
                                fileList.appendChild(fileItem);
                            });
                        });
                }

                function viewFile(filename) {
                    fetch(`/api/file/${filename}`)
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('filename').value = filename;
                            document.getElementById('filecontent').value = data.content;
                            currentFile = filename;
                        });
                }

                function createFile() {
                    const filename = document.getElementById('filename').value;
                    const content = document.getElementById('filecontent').value;
                    
                    fetch('/api/file', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ filename, content })
                    })
                    .then(response => response.json())
                    .then(data => {
                        alert(data.message);
                        loadFiles();
                        document.getElementById('filename').value = '';
                        document.getElementById('filecontent').value = '';
                    });
                }

                function runFile(filename) {
                    const output = document.getElementById('output');
                    output.innerHTML = `⏳ Running ${filename}...`;
                    
                    let command = `./${filename}`;
                    if (filename.endsWith('.py')) command = `python3 ${filename}`;
                    if (filename.endsWith('.js')) command = `node ${filename}`;
                    if (filename.endsWith('.php')) command = `php ${filename}`;
                    if (filename.endsWith('.sh')) command = `bash ${filename}`;
                    
                    fetch('/api/run', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command })
                    })
                    .then(response => response.json())
                    .then(data => {
                        output.innerHTML = `<span class="success">✓ ${filename} executed</span>\n\n${data.output}`;
                        if (data.error) {
                            output.innerHTML += `\n\n<span class="error">✗ Error:</span>\n${data.error}`;
                        }
                        refreshStatus();
                    });
                }

                function deleteFile(filename) {
                    if (confirm(`Delete ${filename}?`)) {
                        fetch('/api/delete', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ filename })
                        })
                        .then(response => response.json())
                        .then(data => {
                            alert(data.message);
                            loadFiles();
                        });
                    }
                }

                function uploadFile() {
                    const fileInput = document.getElementById('fileUpload');
                    const file = fileInput.files[0];
                    
                    if (!file) {
                        alert('Please select a file');
                        return;
                    }
                    
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    fetch('/api/upload', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        alert(data.message);
                        loadFiles();
                        fileInput.value = '';
                    });
                }
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def get_system_status(self):
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # RAM usage
            ram = psutil.virtual_memory()
            ram_used = ram.used
            ram_total = ram.total
            ram_percent = ram.percent
            
            # Disk usage
            disk = psutil.disk_usage('.')
            disk_used = disk.used
            disk_total = disk.total
            disk_percent = disk.percent
            
            # System info
            uptime = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
            platform_info = f"{platform.system()} {platform.release()}"
            process_count = len(psutil.pids())
            cpu_cores = psutil.cpu_count()
            
            status_data = {
                'cpu_usage': round(cpu_usage, 1),
                'ram_used': ram_used,
                'ram_total': ram_total,
                'ram_percent': ram_percent,
                'disk_used': disk_used,
                'disk_total': disk_total,
                'disk_percent': disk_percent,
                'uptime': uptime,
                'platform': platform_info,
                'process_count': process_count,
                'cpu_cores': cpu_cores
            }
            
            self.send_json_response(status_data)
            
        except Exception as e:
            self.send_json_response({'error': f'Status error: {str(e)}'}, 500)
    
    def test_ping(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            host = data.get('host', 'google.com')
            
            # Ping command
            if platform.system().lower() == 'windows':
                command = f"ping -n 1 {host}"
            else:
                command = f"ping -c 1 {host}"
            
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                # Extract ping time from output
                if 'time=' in stdout:
                    ping_time = stdout.split('time=')[1].split(' ')[0]
                    self.send_json_response({
                        'success': True,
                        'ping_time': ping_time,
                        'output': stdout
                    })
                else:
                    self.send_json_response({
                        'success': True,
                        'ping_time': 'Connected',
                        'output': stdout
                    })
            else:
                self.send_json_response({
                    'success': False,
                    'error': stderr or 'Ping failed',
                    'output': stdout
                })
                
        except Exception as e:
            self.send_json_response({'success': False, 'error': str(e)}, 500)
    
    def list_files(self):
        try:
            files = os.listdir('.')
            file_list = [f for f in files if os.path.isfile(f) and not f.startswith('.')]
            self.send_json_response(file_list)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def get_file_content(self):
        try:
            filename = self.path.split('/')[-1]
            if os.path.exists(filename) and os.path.isfile(filename):
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                self.send_json_response({'content': content})
            else:
                self.send_json_response({'error': 'File not found'}, 404)
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def run_command(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            command = data.get('command', '')
            
            # Execute command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            response = {
                'output': stdout,
                'error': stderr,
                'returncode': process.returncode
            }
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def create_file(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            filename = data.get('filename', '')
            content = data.get('content', '')
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Make executable if it's a script
            if filename.endswith(('.sh', '.py')):
                os.chmod(filename, 0o755)
            
            self.send_json_response({'message': f'File {filename} created successfully'})
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def delete_file(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            filename = data.get('filename', '')
            
            if os.path.exists(filename):
                os.remove(filename)
                self.send_json_response({'message': f'File {filename} deleted successfully'})
            else:
                self.send_json_response({'error': 'File not found'}, 404)
                
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def upload_file(self):
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            
            file_item = form['file']
            if file_item.filename:
                filename = os.path.basename(file_item.filename)
                with open(filename, 'wb') as f:
                    f.write(file_item.file.read())
                
                self.send_json_response({'message': f'File {filename} uploaded successfully'})
            else:
                self.send_json_response({'error': 'No file uploaded'}, 400)
                
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def get_local_ip():
    """Get local IP address"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def main():
    PORT = 8080
    
    # Install psutil if not available
    try:
        import psutil
    except ImportError:
        print("Installing psutil...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil
    
    # Get local IP
    local_ip = get_local_ip()
    
    print("🚀 Starting Termux Web Shell Server...")
    print(f"📱 Local: http://localhost:{PORT}")
    print(f"🌐 Network: http://{local_ip}:{PORT}")
    print(f"📊 System monitoring enabled")
    print("📂 Serving from:", os.getcwd())
    print("⏹️  Press Ctrl+C to stop")
    
    with socketserver.TCPServer(("", PORT), WebShellHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()