# Hound Deployment Guide

This guide covers deploying Hound on a Linux touchscreen device.

## Prerequisites

- Linux system (Ubuntu 20.04+ or similar recommended)
- Docker and Docker Compose
- 1920×1080 touchscreen display (recommended)
- Network connectivity for initial setup and external APIs
- At least 4GB RAM and 16GB storage

## Installation

### Automated Installation

1. Clone the repository:
```bash
git clone <repository-url> /tmp/hound
cd /tmp/hound
```

2. Run the installation script:
```bash
sudo ./deploy/scripts/install.sh
```

3. Configure the environment:
```bash
sudo nano /opt/hound/.env
```

Update at minimum:
- `HOUND_SECRET_KEY`: Generate a secure random string
- Other settings can use defaults for initial setup

4. Start the application:
```bash
sudo systemctl start hound
```

### Manual Installation

1. Install dependencies:
```bash
sudo apt-get update
sudo apt-get install -y docker docker-compose curl firefox x11-xserver-utils
```

2. Create installation directory:
```bash
sudo mkdir -p /opt/hound
sudo useradd -r -s /bin/bash -d /opt/hound hound
sudo chown hound:hound /opt/hound
```

3. Copy Hound files:
```bash
sudo cp -r . /opt/hound/
sudo chown -R hound:hound /opt/hound
```

4. Configure environment:
```bash
sudo cp /opt/hound/.env.example /opt/hound/.env
sudo nano /opt/hound/.env
```

5. Start with Docker Compose:
```bash
cd /opt/hound
sudo -u hound docker-compose up -d
```

## Kiosk Mode Configuration

Kiosk mode launches the dashboard in full-screen mode automatically on startup.

### Enable Kiosk Mode

1. Ensure the display manager is configured for auto-login
2. Enable the kiosk service:
```bash
sudo systemctl enable --now hound-kiosk
```

3. Reboot the device

### Kiosk Script Customization

Edit `/opt/hound/deploy/kiosk/hound-kiosk.sh` to:
- Change the browser (Firefox, Chromium, etc.)
- Adjust display resolution
- Modify the dashboard URL

### Alternative Browsers

For Chromium:
```bash
exec chromium --kiosk --incognito "$HOUND_URL"
```

For Epiphany (GNOME Web):
```bash
exec epiphany --application-mode "$HOUND_URL"
```

## Network Configuration

### LAN-Only Access

By default, Hound binds to all interfaces. To restrict to LAN:

1. Edit `docker-compose.yml`:
```yaml
frontend:
  ports:
    - "192.168.1.100:3000:80"  # Replace with your LAN IP
```

2. Configure firewall rules:
```bash
sudo ufw allow from 192.168.1.0/24 to any port 3000
```

### Port Forwarding (Not Recommended)

Do not configure router port forwarding. Hound is designed for LAN-only access.

## Updates

### Automatic Updates

Hound includes a comprehensive automatic update system that runs daily via systemd timer.

**Features:**
- Daily update checks (configurable via systemd timer)
- Automatic backup before updates
- Git-based version tracking
- Health check after update
- Automatic rollback on failure
- Update logging to `/var/log/hound-auto-update.log`

**How it works:**
1. The systemd timer triggers the update script daily
2. The script checks for new commits on the `main` branch
3. If updates are available, it creates a backup
4. Pulls latest changes from GitHub
5. Rebuilds and restarts Docker containers
6. Runs health check
7. Rolls back automatically if health check fails

**Control auto-updates:**
```bash
# Check timer status
sudo systemctl status hound-auto-update.timer

# Enable auto-updates
sudo systemctl enable hound-auto-update.timer

# Disable auto-updates
sudo systemctl disable hound-auto-update.timer

# Trigger update manually
sudo systemctl start hound-auto-update.service

# View update logs
sudo journalctl -u hound-auto-update -f
# Or
sudo tail -f /var/log/hound-auto-update.log
```

**Configure update schedule:**
Edit `/etc/systemd/system/hound-auto-update.timer`:
```ini
[Timer]
OnCalendar=daily              # Run daily
# Or use cron format:
# OnCalendar=*-*-* 02:00      # Run at 2 AM daily
# OnCalendar=Mon              # Run every Monday
# OnCalendar=hourly           # Run every hour
Persistent=true
RandomizedDelaySec=3600
```

Then reload systemd:
```bash
sudo systemctl daemon-reload
sudo systemctl restart hound-auto-update.timer
```

**Backend-based updates:**
The backend also includes an update service that can check for and apply updates via API:
- `/api/system/updates/status` - Get current update status
- `/api/system/updates/check` - Check for available updates
- `/api/system/updates/apply` - Apply available updates

This is controlled by environment variables:
- `HOUND_AUTO_UPDATE_ENABLED`: Enable/disable backend auto-update job
- `HOUND_UPDATE_CHANNEL`: Update channel (stable, beta)
- `HOUND_UPDATE_CHECK_INTERVAL`: How often to check for updates (seconds)

### Manual Update

If you prefer to update manually:

1. Stop services:
```bash
cd /opt/hound
sudo -u hound docker-compose down
```

2. Pull latest code:
```bash
cd /opt/hound
sudo -u hound git pull
```

3. Rebuild and start:
```bash
sudo -u hound docker-compose up -d --build
```

## Backup Configuration

Backups are stored in `/data/backups` (Docker volume).

### Automatic Backups

Configure via environment:
- `HOUND_BACKUP_SCHEDULE`: Cron schedule (default: daily at 2 AM)
- `HOUND_BACKUP_RETENTION_DAYS`: How long to keep backups (default: 30 days)

### Manual Backup

Access the management interface and use the backup feature, or:
```bash
cd /opt/hound
sudo -u hound docker-compose exec backend python -c "
from app.api.backups import create_backup
create_backup()
"
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
cd /opt/hound
sudo -u hound docker-compose logs backend
sudo -u hound docker-compose logs frontend
```

### Database Issues

Check database file:
```bash
sudo -u hound ls -la /var/lib/docker/volumes/hound_hound-data/_data/
```

### Display Issues with Kiosk

1. Check X server is running:
```bash
echo $DISPLAY
ps aux | grep X
```

2. Test browser manually:
```bash
firefox --kiosk http://localhost:3000
```

3. Check systemd service:
```bash
sudo systemctl status hound-kiosk
sudo journalctl -u hound-kiosk -f
```

### Performance Issues

1. Check resource usage:
```bash
docker stats
```

2. Adjust refresh intervals in `.env`:
- `HOUND_WEATHER_REFRESH_INTERVAL`
- `HOUND_BUS_REFRESH_INTERVAL`

3. Reduce photo count or size for screensaver

## Security

### Default Credentials

No default password is shipped. You must create credentials on first access via `/management/setup`.

### Firewall

Configure UFW:
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.1.0/24 to any port 3000
sudo ufw enable
```

### HTTPS (Optional)

For HTTPS, set up a reverse proxy with nginx:
```nginx
server {
    listen 443 ssl;
    server_name hound.local;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
    }
}
```

## Monitoring

### Check Service Status

```bash
sudo systemctl status hound
sudo -u hound docker-compose ps
```

### View Logs

```bash
sudo -u hound docker-compose logs -f
```

### Health Check

```bash
curl http://localhost:3000/api/system/health
```

## Recovery

### Restore from Backup

1. Access management interface → Backups → Restore
2. Or restore manually:
```bash
cd /opt/hound
sudo -u hound docker-compose exec backend python -c "
from app.api.backups import restore_backup
restore_backup(backup_id)
"
```

### Full Reinstall

1. Stop and remove containers:
```bash
cd /opt/hound
sudo -u hound docker-compose down -v
```

2. Remove installation:
```bash
sudo rm -rf /opt/hound
```

3. Re-run installation script
