#!/usr/bin/env python3
"""
Simple HTTP server to serve the ASWP-API frontend (index.html)
"""

import http.server
import socketserver
import os
import sys
import configparser
from pathlib import Path

def load_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    
    # Try to load config from api directory first, then current directory
    config_paths = ['api/config.ini', 'config.ini']
    config_loaded = False
    
    for path in config_paths:
        if os.path.exists(path):
            config.read(path)
            config_loaded = True
            break
    
    if not config_loaded:
        print("Warning: config.ini not found, using defaults")
        # Set defaults
        config.add_section('WEBSERVER')
        config.set('WEBSERVER', 'HOST', '127.0.0.1')
        config.set('WEBSERVER', 'PORT', '8000')
    
    return config

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Request Handler with CORS support"""
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight OPTIONS requests"""
        self.send_response(200)
        self.end_headers()

def main():
    """Start the web server"""
    # Load configuration
    config = load_config()
    
    try:
        host = config.get('WEBSERVER', 'HOST', fallback='127.0.0.1')
        port = int(config.get('WEBSERVER', 'PORT', fallback='8000'))
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        host = '127.0.0.1'
        port = 8000
        print("Using default webserver settings")
    
    # Change to the directory containing index.html (project root)
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Verify index.html exists
    if not os.path.exists('index.html'):
        print("Error: index.html not found in project root")
        print(f"Current directory: {os.getcwd()}")
        print("Available files:", os.listdir('.'))
        sys.exit(1)
    
    try:
        with socketserver.TCPServer((host, port), CORSHTTPRequestHandler) as httpd:
            print(f"🌐 Frontend server running at: http://{host}:{port}")
            print(f"📁 Serving files from: {os.getcwd()}")
            print(f"🔗 Open http://{host}:{port} in your browser")
            print(f"🛑 Press Ctrl+C to stop the server")
            print()
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Error: Port {port} is already in use")
            print(f"   Try using a different port or stop the process using port {port}")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")

if __name__ == "__main__":
    main()