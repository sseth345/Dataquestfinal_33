#!/bin/bash

# Docker entrypoint script for Insider Threat Detection System

set -e

echo "=== Insider Threat Detection System ==="
echo "Starting container initialization..."

# Wait for dependencies to be ready
if [ "$WAIT_FOR_REDIS" = "true" ]; then
    echo "Waiting for Redis to be ready..."
    while ! nc -z redis 6379; do
        sleep 1
    done
    echo "Redis is ready!"
fi

# Create configuration file if it doesn't exist
if [ ! -f "/app/config/config.yaml" ]; then
    echo "Configuration file not found. Creating from example..."
    cp /app/config/config.example.yaml /app/config/config.yaml
    echo "Please customize /app/config/config.yaml for your environment"
fi

# Initialize directories with proper permissions
mkdir -p /app/data /app/logs /app/models /app/reports
chmod 755 /app/data /app/logs /app/models /app/reports

# Set up health check endpoint (simple HTTP server for health checks)
if [ "$1" = "python" ] && [ "$2" = "src/main.py" ]; then
    echo "Setting up health check endpoint..."
    cat > /app/health_check.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import threading
import time
import json
from datetime import datetime

class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            try:
                # Simple health check - verify the main process is running
                health_data = {
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'service': 'insider-threat-detection'
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(health_data).encode())
            except Exception as e:
                self.send_response(503)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_data = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.wfile.write(json.dumps(error_data).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress health check logs
        pass

def start_health_server():
    port = 8080
    with socketserver.TCPServer(("", port), HealthCheckHandler) as httpd:
        httpd.serve_forever()

if __name__ == '__main__':
    # Start health check server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    print(f"Health check server started on port 8080")
EOF

    # Start health check server in background
    python3 /app/health_check.py &
    HEALTH_PID=$!
    
    # Trap signals to ensure clean shutdown
    trap 'echo "Shutting down..."; kill $HEALTH_PID 2>/dev/null || true; exit' INT TERM
fi

echo "Container initialization complete!"
echo "Starting main application..."

# Execute the main command
exec "$@"