#!/usr/bin/env python3
import http.server
import socketserver
import os
import subprocess
import json
import cgi
import threading
from pathlib import Path

class WebShellHandler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/':
            self.send_html_interface()
        elif self.path == '/api/files':
            self.list_files()
        elif self.path.startswith('/api/file/'):
            self.get_file_content()
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
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Termux Web Shell Server</h1>
                    <p>Current Directory: <span id="currentDir"></span></p>
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
                
                // Load initial data
                document.addEventListener('DOMContentLoaded', function() {
                    loadFiles();
                    getCurrentDir();
                });

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
    
    # Get local IP
    local_ip = get_local_ip()
    
    print("🚀 Starting Termux Web Shell Server...")
    print(f"📱 Local: http://localhost:{PORT}")
    print(f"🌐 Network: http://{local_ip}:{PORT}")
    print("📂 Serving from:", os.getcwd())
    print("⏹️  Press Ctrl+C to stop")
    
    with socketserver.TCPServer(("", PORT), WebShellHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    main()
