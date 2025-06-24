import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = 'filesharing'

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# SSL Configuration
# keyfile = 'path/to/keyfile'
# certfile = 'path/to/certfile'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs') 