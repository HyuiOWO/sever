#!/usr/bin/env python3
import http.server
import socketserver
import os
import subprocess
import json
import threading
import time
import platform
from pathlib import Path
import datetime
import sys
import urllib.parse
import tempfile

class WebShellHandler(http.server.SimpleHTTPRequestHandler):
    
    # Biến để lưu thời gian bắt đầu
    start_time = datetime.datetime.now()
    
    # Biến để quản lý process đang chạy và log files
    running_processes = {}
    process_logs = {}  # Lưu log file path cho mỗi process
    
    def do_GET(self):
        if self.path == '/':
            self.send_html_interface()
        elif self.path == '/api/files':
            self.list_files()
        elif self.path.startswith('/api/file/'):
            self.get_file_content()
        elif self.path == '/api/status':
            self.get_system_status()
        elif self.path == '/api/running':
            self.get_running_processes()
        elif self.path.startswith('/api/log/'):
            self.get_process_log()
        else:
            super().do_GET()
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        
        if self.path == '/api/run':
            self.run_command(post_data)
        elif self.path == '/api/file':
            self.create_file(post_data)
        elif self.path == '/api/upload':
            self.upload_file(post_data)
        elif self.path == '/api/delete':
            self.delete_file(post_data)
        elif self.path == '/api/ping':
            self.test_ping(post_data)
        elif self.path == '/api/stop':
            self.stop_process(post_data)
        else:
            self.send_error(404)
    
    def send_html_interface(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Termux Web Shell Server</title>
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
                    align-items: center;
                }
                .file-item:hover { background: #3d3d3d; }
                .file-actions button { 
                    width: auto; 
                    padding: 4px 10px; 
                    margin-left: 5px; 
                    font-size: 12px;
                }
                .run-btn { background: #006600; }
                .stop-btn { background: #cc0000; }
                .stop-btn:hover { background: #ff0000; }
                .log-btn { background: #0088cc; }
                .log-btn:hover { background: #00aaff; }
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
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 15px;
                    margin-top: 10px;
                }
                .status-item {
                    background: #1a1a1a;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #00ff00;
                    text-align: center;
                }
                .status-label {
                    font-size: 14px;
                    color: #888;
                    margin-bottom: 8px;
                }
                .status-value {
                    font-size: 16px;
                    font-weight: bold;
                    color: #00ff00;
                }
                
                .refresh-btn {
                    background: #0088cc;
                    padding: 8px 15px;
                    font-size: 14px;
                    margin-top: 15px;
                    width: auto;
                }
                .refresh-btn:hover { background: #00aaff; }
                
                .ping-test {
                    background: #006600;
                    padding: 8px 15px;
                    font-size: 14px;
                    margin-top: 10px;
                    width: auto;
                }
                .ping-test:hover { background: #008800; }
                
                /* Loading Animation */
                .loading {
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    border: 3px solid #ffffff33;
                    border-radius: 50%;
                    border-top-color: #00ff00;
                    animation: spin 1s ease-in-out infinite;
                    margin-right: 10px;
                }
                
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                
                .pulse {
                    animation: pulse 1.5s infinite;
                }
                
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
                
                .command-status {
                    background: #004400;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 0;
                    border-left: 4px solid #00ff00;
                }
                
                .live-output {
                    background: #000;
                    border: 1px solid #00ff00;
                    padding: 10px;
                    border-radius: 5px;
                    max-height: 300px;
                    overflow-y: auto;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                }
                
                .running-processes {
                    background: #002200;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 0;
                    border-left: 4px solid #00ff00;
                }
                
                .process-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 5px;
                    border-bottom: 1px solid #004400;
                }
                
                .process-info {
                    flex: 1;
                }
                
                .process-actions {
                    display: flex;
                    gap: 5px;
                }
                
                .log-modal {
                    display: none;
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: #1e1e1e;
                    border: 2px solid #00ff00;
                    border-radius: 10px;
                    padding: 20px;
                    z-index: 1000;
                    width: 90%;
                    max-width: 800px;
                    max-height: 80vh;
                    box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
                }
                
                .log-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                    border-bottom: 1px solid #00ff00;
                    padding-bottom: 10px;
                }
                
                .log-content {
                    background: #000;
                    color: #00ff00;
                    padding: 15px;
                    border-radius: 5px;
                    max-height: 60vh;
                    overflow-y: auto;
                    font-family: 'Courier New', monospace;
                    white-space: pre-wrap;
                    font-size: 12px;
                }
                
                .close-btn {
                    background: #cc0000;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    cursor: pointer;
                }
                
                .close-btn:hover {
                    background: #ff0000;
                }
                
                .overlay {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.8);
                    z-index: 999;
                }
                
                .refresh-log-btn {
                    background: #0088cc;
                    padding: 5px 10px;
                    font-size: 12px;
                    margin-left: 10px;
                }
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
                                    <div class="status-label">⏰ Server Uptime</div>
                                    <div class="status-value" id="uptime">Loading...</div>
                                </div>
                                <div class="status-item">
                                    <div class="status-label">🌐 Network Ping</div>
                                    <div class="status-value" id="pingStatus">Click to test</div>
                                    <button class="ping-test" onclick="testPing()">Test Ping Google</button>
                                </div>
                            </div>
                            
                            <!-- Running Processes -->
                            <div class="running-processes" id="runningProcesses" style="display: none;">
                                <h4>🔄 Running Processes:</h4>
                                <div id="processList"></div>
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
                            <option value="shell">Shell Command (Blocking)</option>
                            <option value="shell-bg">Shell Command (Background)</option>
                            <option value="python">Python Script</option>
                            <option value="node">Node.js</option>
                            <option value="php">PHP</option>
                            <option value="bash">Bash Script</option>
                        </select>
                        <textarea id="command" placeholder="Enter command or code..." rows="5"></textarea>
                        <button onclick="runCommand()">▶ Run Command</button>
                        
                        <!-- Command Status -->
                        <div id="commandStatus" style="display: none;">
                            <div class="command-status">
                                <div class="loading"></div>
                                <span id="statusText">Executing command...</span>
                            </div>
                            <div class="live-output" id="liveOutput">
                                <div class="pulse">Waiting for output...</div>
                            </div>
                        </div>
                        
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

            <!-- Log Modal -->
            <div class="overlay" id="overlay" onclick="closeLogModal()"></div>
            <div class="log-modal" id="logModal">
                <div class="log-header">
                    <h3>📋 Process Log: <span id="logTitle"></span></h3>
                    <div>
                        <button class="refresh-log-btn" onclick="refreshCurrentLog()">🔄 Refresh</button>
                        <button class="close-btn" onclick="closeLogModal()">✕ Close</button>
                    </div>
                </div>
                <div class="log-content" id="logContent">
                    Loading log content...
                </div>
            </div>

            <script>
                let currentFile = '';
                let statusInterval;
                let commandRunning = false;
                let runningFiles = {};
                let currentLogFile = '';
                let logRefreshInterval = null;
                
                // Load initial data
                document.addEventListener('DOMContentLoaded', function() {
                    loadFiles();
                    getCurrentDir();
                    refreshStatus();
                    updateServerTime();
                    checkRunningProcesses();
                    
                    // Auto refresh status every 5 seconds
                    statusInterval = setInterval(refreshStatus, 5000);
                    setInterval(updateServerTime, 1000);
                    setInterval(checkRunningProcesses, 3000);
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
                        document.getElementById('currentDir').textContent = data.output.trim();
                    });
                }

                function refreshStatus() {
                    fetch('/api/status')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('uptime').textContent = data.uptime;
                        })
                        .catch(error => {
                            console.error('Status update failed:', error);
                        });
                }

                function checkRunningProcesses() {
                    fetch('/api/running')
                        .then(response => response.json())
                        .then(data => {
                            const processesContainer = document.getElementById('runningProcesses');
                            const processList = document.getElementById('processList');
                            
                            if (data.processes && Object.keys(data.processes).length > 0) {
                                processesContainer.style.display = 'block';
                                processList.innerHTML = '';
                                
                                Object.entries(data.processes).forEach(([filename, processInfo]) => {
                                    const processItem = document.createElement('div');
                                    processItem.className = 'process-item';
                                    processItem.innerHTML = `
                                        <div class="process-info">
                                            <strong>📄 ${filename}</strong><br>
                                            <small>PID: ${processInfo.pid} | Started: ${processInfo.start_time}</small>
                                        </div>
                                        <div class="process-actions">
                                            <button class="log-btn" onclick="viewProcessLog('${filename}')">📋 View Log</button>
                                            <button class="stop-btn" onclick="stopProcess('${filename}')">🛑 Stop</button>
                                        </div>
                                    `;
                                    processList.appendChild(processItem);
                                });
                            } else {
                                processesContainer.style.display = 'none';
                            }
                        })
                        .catch(error => {
                            console.error('Check processes failed:', error);
                        });
                }

                function viewProcessLog(filename) {
                    currentLogFile = filename;
                    document.getElementById('logTitle').textContent = filename;
                    document.getElementById('logModal').style.display = 'block';
                    document.getElementById('overlay').style.display = 'block';
                    
                    refreshCurrentLog();
                    
                    // Auto-refresh log every 2 seconds
                    if (logRefreshInterval) {
                        clearInterval(logRefreshInterval);
                    }
                    logRefreshInterval = setInterval(refreshCurrentLog, 2000);
                }

                function refreshCurrentLog() {
                    if (!currentLogFile) return;
                    
                    fetch(`/api/log/${currentLogFile}`)
                        .then(response => response.json())
                        .then(data => {
                            const logContent = document.getElementById('logContent');
                            if (data.success) {
                                logContent.textContent = data.log || 'No output yet...';
                                // Auto scroll to bottom
                                logContent.scrollTop = logContent.scrollHeight;
                            } else {
                                logContent.textContent = `Error: ${data.error}`;
                            }
                        })
                        .catch(error => {
                            document.getElementById('logContent').textContent = `Failed to load log: ${error}`;
                        });
                }

                function closeLogModal() {
                    document.getElementById('logModal').style.display = 'none';
                    document.getElementById('overlay').style.display = 'none';
                    currentLogFile = '';
                    
                    if (logRefreshInterval) {
                        clearInterval(logRefreshInterval);
                        logRefreshInterval = null;
                    }
                }

                function stopProcess(filename) {
                    if (confirm(`Stop ${filename}?`)) {
                        fetch('/api/stop', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ filename: filename })
                        })
                        .then(response => response.json())
                        .then(data => {
                            alert(data.message);
                            checkRunningProcesses();
                            loadFiles(); // Refresh file list to update buttons
                            
                            // Close log modal if viewing this process
                            if (currentLogFile === filename) {
                                closeLogModal();
                            }
                        })
                        .catch(error => {
                            alert('Error stopping process: ' + error);
                        });
                    }
                }

                function testPing() {
                    const pingElement = document.getElementById('pingStatus');
                    pingElement.innerHTML = '<div class="loading"></div>Testing ping...';
                    
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
                    if (commandRunning) {
                        alert('Please wait for the current command to finish...');
                        return;
                    }
                    
                    const commandType = document.getElementById('commandType').value;
                    const command = document.getElementById('command').value;
                    const output = document.getElementById('output');
                    const commandStatus = document.getElementById('commandStatus');
                    const liveOutput = document.getElementById('liveOutput');
                    
                    if (!command.trim()) {
                        alert('Please enter a command');
                        return;
                    }
                    
                    // Hiển thị trạng thái đang chạy
                    commandRunning = true;
                    commandStatus.style.display = 'block';
                    output.innerHTML = '';
                    liveOutput.innerHTML = '<div class="pulse">Starting command execution...</div>';
                    
                    let finalCommand = command;
                    let isBackground = false;
                    
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
                        case 'shell-bg':
                            finalCommand = command;
                            isBackground = true;
                            break;
                        default:
                            finalCommand = command;
                    }
                    
                    // Cập nhật trạng thái
                    document.getElementById('statusText').textContent = `Executing: ${finalCommand}`;
                    
                    // Tạo hiệu ứng loading real-time
                    let dots = 0;
                    const loadingInterval = setInterval(() => {
                        dots = (dots + 1) % 4;
                        const statusElement = document.getElementById('statusText');
                        if (statusElement) {
                            statusElement.textContent = `Executing${'.'.repeat(dots)}`;
                        }
                    }, 500);
                    
                    const requestBody = {
                        command: finalCommand,
                        background: isBackground
                    };
                    
                    fetch('/api/run', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(requestBody)
                    })
                    .then(response => response.json())
                    .then(data => {
                        clearInterval(loadingInterval);
                        commandRunning = false;
                        
                        if (data.background) {
                            // Background process
                            output.innerHTML = `<span class="success">✓ Command started in background (PID: ${data.pid})</span>`;
                            liveOutput.innerHTML = `<div class="success">Background process started ✓</div>`;
                            checkRunningProcesses();
                        } else {
                            // Normal process
                            let resultHTML = `<span class="success">✓ Command completed successfully</span>\n\n`;
                            resultHTML += `<strong>Output:</strong>\n${data.output}`;
                            
                            if (data.error) {
                                resultHTML += `\n\n<span class="error">✗ Errors:</span>\n${data.error}`;
                            }
                            
                            output.innerHTML = resultHTML;
                            liveOutput.innerHTML = `<div class="success">Command completed ✓</div>`;
                        }
                        
                        // Ẩn status sau 3 giây
                        setTimeout(() => {
                            commandStatus.style.display = 'none';
                        }, 3000);
                        
                        loadFiles();
                        refreshStatus();
                    })
                    .catch(error => {
                        clearInterval(loadingInterval);
                        commandRunning = false;
                        output.innerHTML = `<span class="error">✗ Request failed: ${error}</span>`;
                        liveOutput.innerHTML = `<div class="error">Command failed ✗</div>`;
                        
                        setTimeout(() => {
                            commandStatus.style.display = 'none';
                        }, 3000);
                    });
                }

                function loadFiles() {
                    fetch('/api/files')
                        .then(response => response.json())
                        .then(files => {
                            const fileList = document.getElementById('fileList');
                            fileList.innerHTML = '<h4>Files in current directory:</h4>';
                            
                            // Get running processes to update buttons
                            fetch('/api/running')
                                .then(r => r.json())
                                .then(processData => {
                                    const runningProcesses = processData.processes || {};
                                    
                                    files.forEach(file => {
                                        const fileItem = document.createElement('div');
                                        fileItem.className = 'file-item';
                                        
                                        const isRunning = runningProcesses[file];
                                        const buttonText = isRunning ? '🛑 Stop' : '▶ Run';
                                        const buttonClass = isRunning ? 'stop-btn' : 'run-btn';
                                        
                                        fileItem.innerHTML = `
                                            <span onclick="viewFile('${file}')">📄 ${file}</span>
                                            <div class="file-actions">
                                                ${isRunning ? `
                                                    <button class="log-btn" onclick="viewProcessLog('${file}')">📋 Log</button>
                                                    <button class="${buttonClass}" onclick="stopProcess('${file}')">${buttonText}</button>
                                                ` : `
                                                    <button class="${buttonClass}" onclick="runFile('${file}')">${buttonText}</button>
                                                `}
                                                <button onclick="deleteFile('${file}')">Delete</button>
                                            </div>
                                        `;
                                        fileList.appendChild(fileItem);
                                    });
                                })
                                .catch(error => {
                                    console.error('Error loading running processes:', error);
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
                    
                    if (!filename.trim()) {
                        alert('Please enter a filename');
                        return;
                    }
                    
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
                    if (commandRunning) {
                        alert('Please wait for the current command to finish...');
                        return;
                    }
                    
                    const output = document.getElementById('output');
                    const commandStatus = document.getElementById('commandStatus');
                    const liveOutput = document.getElementById('liveOutput');
                    
                    commandRunning = true;
                    commandStatus.style.display = 'block';
                    output.innerHTML = '';
                    liveOutput.innerHTML = '<div class="pulse">Preparing to run file...</div>';
                    
                    let command = '';
                    if (filename.endsWith('.py')) command = `python3 ${filename}`;
                    else if (filename.endsWith('.js')) command = `node ${filename}`;
                    else if (filename.endsWith('.php')) command = `php ${filename}`;
                    else if (filename.endsWith('.sh')) command = `bash ${filename}`;
                    else command = `./${filename}`;
                    
                    document.getElementById('statusText').textContent = `Running: ${command}`;
                    
                    let dots = 0;
                    const loadingInterval = setInterval(() => {
                        dots = (dots + 1) % 4;
                        document.getElementById('statusText').textContent = `Running${'.'.repeat(dots)}`;
                    }, 500);
                    
                    // Run in background to avoid blocking web server
                    const requestBody = {
                        command: command,
                        background: true,
                        filename: filename
                    };
                    
                    fetch('/api/run', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(requestBody)
                    })
                    .then(response => response.json())
                    .then(data => {
                        clearInterval(loadingInterval);
                        commandRunning = false;
                        
                        if (data.background) {
                            output.innerHTML = `<span class="success">✓ ${filename} started in background (PID: ${data.pid})</span>`;
                            liveOutput.innerHTML = `<div class="success">File running in background ✓</div>`;
                        } else {
                            let resultHTML = `<span class="success">✓ ${filename} executed</span>\n\n`;
                            resultHTML += `<strong>Output:</strong>\n${data.output}`;
                            
                            if (data.error) {
                                resultHTML += `\n\n<span class="error">✗ Errors:</span>\n${data.error}`;
                            }
                            
                            output.innerHTML = resultHTML;
                            liveOutput.innerHTML = `<div class="success">File execution completed ✓</div>`;
                        }
                        
                        setTimeout(() => {
                            commandStatus.style.display = 'none';
                        }, 3000);
                        
                        loadFiles(); // Refresh to update buttons
                        checkRunningProcesses();
                        refreshStatus();
                    })
                    .catch(error => {
                        clearInterval(loadingInterval);
                        commandRunning = false;
                        output.innerHTML = `<span class="error">✗ Failed to run file: ${error}</span>`;
                        liveOutput.innerHTML = `<div class="error">File execution failed ✗</div>`;
                        
                        setTimeout(() => {
                            commandStatus.style.display = 'none';
                        }, 3000);
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
                        // Close log modal if viewing this file
                            if (currentLogFile === filename) {
                                closeLogModal();
                            }
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
            # Tính thời gian uptime
            current_time = datetime.datetime.now()
            uptime_delta = current_time - self.start_time
            uptime_str = str(uptime_delta).split('.')[0]  # Bỏ phần microseconds
            
            status_data = {
                'uptime': uptime_str,
                'start_time': self.start_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.send_json_response(status_data)
            
        except Exception as e:
            self.send_json_response({'error': f'Status error: {str(e)}'}, 500)
    
    def get_running_processes(self):
        """Get list of running processes"""
        try:
            processes_info = {}
            for filename, process_info in self.running_processes.items():
                processes_info[filename] = {
                    'pid': process_info['pid'],
                    'start_time': process_info['start_time']
                }
            
            self.send_json_response({
                'processes': processes_info
            })
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def get_process_log(self):
        """Get log content for a running process"""
        try:
            filename = self.path.split('/')[-1]
            
            if filename in self.running_processes:
                log_file = self.running_processes[filename]['log_file']
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()
                    self.send_json_response({
                        'success': True,
                        'log': log_content
                    })
                else:
                    self.send_json_response({
                        'success': True,
                        'log': 'Log file not found or no output yet...'
                    })
            else:
                self.send_json_response({
                    'success': False,
                    'error': 'Process not found or not running'
                })
                
        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': f'Error reading log: {str(e)}'
            }, 500)
    
    def stop_process(self, post_data):
        """Stop a running process"""
        try:
            data = json.loads(post_data.decode('utf-8'))
            filename = data.get('filename', '')
            
            if filename in self.running_processes:
                process_info = self.running_processes[filename]
                pid = process_info['pid']
                log_file = process_info['log_file']
                
                try:
                    # Kill the process
                    os.kill(pid, 9)
                    # Remove log file
                    if os.path.exists(log_file):
                        os.remove(log_file)
                    # Remove from running processes
                    del self.running_processes[filename]
                    self.send_json_response({'message': f'Stopped {filename} (PID: {pid})'})
                except ProcessLookupError:
                    # Process already dead
                    if os.path.exists(log_file):
                        os.remove(log_file)
                    del self.running_processes[filename]
                    self.send_json_response({'message': f'Process {filename} was already stopped'})
                except Exception as e:
                    self.send_json_response({'error': f'Error stopping process: {str(e)}'}, 500)
            else:
                self.send_json_response({'error': 'Process not found'}, 404)
                
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def test_ping(self, post_data):
        try:
            data = json.loads(post_data.decode('utf-8'))
            host = data.get('host', 'google.com')
            
            # Ping command
            if platform.system().lower() == 'windows':
                command = f"ping -n 2 {host}"
            else:
                command = f"ping -c 2 {host}"
            
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
    
    def run_command(self, post_data):
        try:
            data = json.loads(post_data.decode('utf-8'))
            command = data.get('command', '')
            run_in_background = data.get('background', False)
            filename = data.get('filename', '')
            
            if run_in_background:
                # Tạo log file cho process
                log_file = f"/tmp/{filename}_{int(time.time())}.log"
                
                # Run command in background và redirect output to log file
                process = subprocess.Popen(
                    f"{command} > {log_file} 2>&1 & echo $!",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    pid = int(stdout.strip())
                    # Lưu thông tin process
                    self.running_processes[filename] = {
                        'pid': pid,
                        'log_file': log_file,
                        'start_time': datetime.datetime.now().strftime("%H:%M:%S")
                    }
                    
                    response = {
                        'background': True,
                        'pid': pid,
                        'filename': filename,
                        'message': f'Process started with PID: {pid}'
                    }
                    self.send_json_response(response)
                else:
                    self.send_json_response({
                        'error': f'Failed to start process: {stderr}'
                    }, 500)
                
            else:
                # Run command normally (blocking)
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
                    'returncode': process.returncode,
                    'background': False
                }
                self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def create_file(self, post_data):
        try:
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
    
    def delete_file(self, post_data):
        try:
            data = json.loads(post_data.decode('utf-8'))
            filename = data.get('filename', '')
            
            if os.path.exists(filename):
                os.remove(filename)
                self.send_json_response({'message': f'File {filename} deleted successfully'})
            else:
                self.send_json_response({'error': 'File not found'}, 404)
                
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def upload_file(self, post_data):
        try:
            # Simple file upload implementation
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' in content_type:
                # Parse filename from multipart data
                lines = post_data.split(b'\r\n')
                filename = None
                for i, line in enumerate(lines):
                    if b'filename="' in line:
                        filename = line.split(b'filename="')[1].split(b'"')[0].decode()
                        # File content starts after two lines
                        file_content = b'\r\n'.join(lines[i+3:-2])
                        break
                
                if filename:
                    with open(filename, 'wb') as f:
                        f.write(file_content)
                    self.send_json_response({'message': f'File {filename} uploaded successfully'})
                else:
                    self.send_json_response({'error': 'No file found in upload'}, 400)
            else:
                self.send_json_response({'error': 'Invalid content type'}, 400)
                
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
    print(f"⏰ Server started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📂 Serving from:", os.getcwd())
    print("🔥 Background processes with LOGS enabled")
    print("⏹️  Press Ctrl+C to stop")
    
    with socketserver.TCPServer(("", PORT), WebShellHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
            # Kill all running processes when server stops
            for filename, process_info in WebShellHandler.running_processes.items():
                try:
                    os.kill(process_info['pid'], 9)
                    # Remove log file
                    if os.path.exists(process_info['log_file']):
                        os.remove(process_info['log_file'])
                    print(f"🛑 Killed {filename} (PID: {process_info['pid']})")
                except:
                    pass

if __name__ == "__main__":
    main()