# Deployment Guide

## Prerequisites
- Python 3.8 or higher
- PostgreSQL
- Nginx
- Domain name (for SSL)

## Production Deployment Steps

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3-pip python3-venv nginx postgresql
```

### 2. Create Application Directory
```bash
# Create application directory
sudo mkdir -p /var/www/filesharing
sudo chown -R $USER:$USER /var/www/filesharing
```

### 3. Setup Virtual Environment
```bash
# Create and activate virtual environment
python3 -m venv /var/www/filesharing/venv
source /var/www/filesharing/venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 4. Environment Configuration
1. Copy `.env` file to production server
2. Update environment variables:
   - Set `DEBUG=False`
   - Update `DATABASE_URL`
   - Configure mail settings
   - Set secure `SECRET_KEY`

### 5. Database Setup
```bash
# Initialize database
flask db upgrade
```

### 6. Gunicorn Setup
1. Copy `gunicorn_config.py` to production directory
2. Copy `filesharing.service` to `/etc/systemd/system/`
3. Start the service:
```bash
sudo systemctl start filesharing
sudo systemctl enable filesharing
```

### 7. Nginx Configuration
1. Create Nginx configuration:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /uploads {
        internal;
        alias /var/www/filesharing/uploads;
    }
}
```

### 8. SSL Setup (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your_domain.com
```

### 9. Security Checklist
- [ ] All passwords are strong and secure
- [ ] Debug mode is disabled
- [ ] SSL is properly configured
- [ ] File permissions are correct
- [ ] Database backups are configured
- [ ] Logging is properly set up

### 10. Monitoring Setup
- Set up monitoring using your preferred tool (e.g., Prometheus, Grafana)
- Configure log rotation
- Set up backup system

### 11. Maintenance
- Regular database backups
- Log rotation
- System updates
- SSL certificate renewal

## Troubleshooting

### Common Issues
1. Permission errors:
   ```bash
   sudo chown -R www-data:www-data /var/www/filesharing/uploads
   sudo chmod -R 755 /var/www/filesharing
   ```

2. Database connection issues:
   - Check PostgreSQL is running
   - Verify connection string
   - Check firewall settings

3. Nginx errors:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Logging
- Application logs: `/var/www/filesharing/logs/`
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u filesharing` 