# Hound Troubleshooting Guide

This guide covers common issues and their solutions.

## General Issues

### Application Won't Start

**Symptoms**: Containers fail to start or restart repeatedly

**Solutions**:
1. Check container status:
```bash
cd /opt/hound
sudo -u hound docker-compose ps
```

2. View logs:
```bash
sudo -u hound docker-compose logs backend
sudo -u hound docker-compose logs frontend
```

3. Check Docker is running:
```bash
sudo systemctl status docker
```

4. Verify environment file exists:
```bash
ls -la /opt/hound/.env
```

5. Check port conflicts:
```bash
sudo netstat -tlnp | grep -E ':(3000|8000)'
```

### Cannot Access Dashboard

**Symptoms**: Browser cannot connect to `http://<device-ip>:3000`

**Solutions**:
1. Verify containers are running:
```bash
sudo -u hound docker-compose ps
```

2. Check firewall:
```bash
sudo ufw status
sudo ufw allow 3000/tcp
```

3. Test locally on the device:
```bash
curl http://localhost:3000
```

4. Check network connectivity:
```bash
ping <device-ip>
```

5. Verify frontend health:
```bash
curl http://localhost:3000/health
```

## Authentication Issues

### Cannot Access Management Interface

**Symptoms**: Redirected to login page, login fails

**Solutions**:
1. Verify credential is set up:
```bash
sudo -u hound docker-compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.credential import Credential
db = SessionLocal()
print(db.query(Credential).count())
"
```

2. Reset credential if needed (requires database access):
```bash
sudo -u hound docker-compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.credential import Credential
from app.core.security import get_password_hash
db = SessionLocal()
db.query(Credential).delete()
db.add(Credential(hashed_password=get_password_hash('newpassword')))
db.commit()
"
```

3. Clear browser cookies and localStorage

4. Check for too many failed attempts (15-minute lockout):
```bash
sudo -u hound docker-compose exec backend python -c "
from app.core.database import SessionLocal
from app.models.credential import Credential
from datetime import datetime, timedelta
db = SessionLocal()
cred = db.query(Credential).first()
if cred and cred.failed_attempts >= 5:
    cred.failed_attempts = 0
    cred.last_failed_attempt = None
    db.commit()
"
```

## Weather Issues

### Weather Not Displaying

**Symptoms**: Weather card shows "unavailable" or "stale"

**Solutions**:
1. Check weather location is configured:
   - Access management interface → Weather
   - Verify location is set

2. Test network connectivity:
```bash
curl https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.1&current=temperature_2m
```

3. Check refresh interval:
```bash
grep HOUND_WEATHER_REFRESH_INTERVAL /opt/hound/.env
```

4. View system status:
   - Access management interface → System Status
   - Check weather component status

5. Restart backend:
```bash
sudo -u hound docker-compose restart backend
```

### Weather Data Stale

**Symptoms**: Weather shows as stale, not updating

**Solutions**:
1. Check last update time in system status
2. Verify network connectivity
3. Check Open-Meteo API status
4. Reduce refresh interval temporarily to test

## Bus Issues

### Bus Departures Not Showing

**Symptoms**: Bus card shows "unavailable" or no departures

**Solutions**:
1. Verify bus stops are configured:
   - Access management interface → Bus Stops
   - Check stops are enabled

2. Test Bustimes API:
```bash
curl https://bustimes.org/stops/<ATCO_CODE>/times.json
```

3. Verify ATCO codes are correct
4. Check system status for bus component errors
5. Verify network connectivity

### Incorrect Bus Times

**Symptoms**: Departure times or countdowns are wrong

**Solutions**:
1. Check device timezone:
```bash
timedatectl
```

2. Verify timezone in `.env`:
```bash
grep HOUND_TIMEZONE /opt/hound/.env
```

3. Restart backend after timezone change:
```bash
sudo -u hound docker-compose restart backend
```

## Calendar Issues

### Events Not Displaying

**Symptoms**: Calendar or agenda shows no events

**Solutions**:
1. Verify events exist:
   - Access management interface → Calendar
   - Check events are created

2. Check event dates are in the displayed range
3. Verify timezone handling for all-day events
4. Check category colours are configured

### Recurring Events Not Working

**Symptoms**: Recurring events don't generate occurrences

**Solutions**:
1. Verify recurrence rule is set:
   - Edit event → check recurrence settings
   - Verify frequency, interval, and end date

2. Check system status for errors
3. Test with simple daily recurrence first
4. Verify date calculations with leap years

## Screensaver Issues

### Screensaver Not Activating

**Symptoms**: Display stays on dashboard indefinitely

**Solutions**:
1. Check inactivity timeout:
```bash
grep HOUND_SCREENSAVER_TIMEOUT /opt/hound/.env
```

2. Verify photos are uploaded:
   - Access management interface → Photos
   - Check photo count

3. Test by waiting without interaction
4. Check browser console for JavaScript errors

### Photos Not Rotating

**Symptoms**: Same photo displayed continuously

**Solutions**:
1. Check photo rotation interval:
```bash
grep HOUND_PHOTO_ROTATION_INTERVAL /opt/hound/.env
```

2. Verify multiple photos are uploaded
3. Check photo file sizes are reasonable
4. Review browser console for errors

### Dimming Not Working

**Symptoms**: Screensaver doesn't dim overnight

**Solutions**:
1. Check dimming times:
```bash
grep HOUND_DIMMING_START /opt/hound/.env
grep HOUND_DIMMING_END /opt/hound/.env
```

2. Verify device timezone is correct
3. Check current time against dimming schedule
4. Test by adjusting dimming times temporarily

## Backup Issues

### Backups Not Running

**Symptoms**: No automatic backups created

**Solutions**:
1. Check backup schedule format:
```bash
grep HOUND_BACKUP_SCHEDULE /opt/hound/.env
```

2. Verify backup directory permissions:
```bash
sudo -u hound ls -la /var/lib/docker/volumes/hound_hound-data/_data/backups
```

3. Check system status for backup errors
4. Test manual backup from management interface

### Restore Fails

**Symptoms**: Backup restore fails with error

**Solutions**:
1. Verify backup file exists and is valid
2. Check backup file integrity
3. Ensure sufficient disk space
4. Review error message in management interface
5. Check safety backup was created

## Database Issues

### Database Locked

**Symptoms**: "database is locked" errors

**Solutions**:
1. Check for long-running transactions
2. Restart backend:
```bash
sudo -u hound docker-compose restart backend
```

3. Check disk space:
```bash
df -h
```

4. Verify WAL mode is enabled (default)

### Database Corruption

**Symptoms**: Queries fail, data appears missing

**Solutions**:
1. Restore from recent backup
2. Check database file integrity:
```bash
sudo -u hound docker-compose exec backend sqlite3 /data/hound.db "PRAGMA integrity_check;"
```

3. If corruption detected, restore from backup

## Kiosk Issues

### Kiosk Browser Won't Start

**Symptoms**: Display stays at desktop, no browser

**Solutions**:
1. Check kiosk service status:
```bash
sudo systemctl status hound-kiosk
```

2. View kiosk service logs:
```bash
sudo journalctl -u hound-kiosk -f
```

3. Test browser manually:
```bash
firefox --kiosk http://localhost:3000
```

4. Verify X server is running:
```bash
echo $DISPLAY
ps aux | grep X
```

5. Check user permissions for display

### Browser Crashes

**Symptoms**: Browser opens then closes repeatedly

**Solutions**:
1. Check browser logs
2. Try different browser (Chromium, Epiphany)
3. Reduce photo size or count
4. Check system resources:
```bash
free -h
top
```

## Performance Issues

### Slow Dashboard

**Symptoms**: Dashboard loads slowly, animations lag

**Solutions**:
1. Check system resources:
```bash
docker stats
```

2. Reduce refresh intervals in `.env`
3. Reduce photo count or optimize images
4. Check network latency for external APIs
5. Consider upgrading hardware if resources are limited

### High Memory Usage

**Symptoms**: System becomes unresponsive, high memory consumption

**Solutions**:
1. Check memory usage:
```bash
free -h
docker stats
```

2. Reduce refresh intervals
3. Limit photo count in screensaver
4. Restart containers:
```bash
sudo -u hound docker-compose restart
```

## Network Issues

### Cannot Access from Other Devices

**Symptoms**: Dashboard accessible on device but not from LAN

**Solutions**:
1. Check device IP:
```bash
ip addr show
```

2. Verify containers are binding correctly:
```bash
sudo -u hound docker-compose ps
```

3. Check firewall:
```bash
sudo ufw status
sudo ufw allow from 192.168.1.0/24 to any port 3000
```

4. Test from another device:
```bash
ping <device-ip>
curl http://<device-ip>:3000
```

### External APIs Unreachable

**Symptoms**: Weather and bus data unavailable

**Solutions**:
1. Test internet connectivity:
```bash
ping 8.8.8.8
curl https://www.google.com
```

2. Check DNS:
```bash
nslookup api.open-meteo.com
```

3. Verify network configuration
4. Check router settings

## Recovery Procedures

### Full System Reset

If all else fails, perform a full reset:

1. Stop and remove containers:
```bash
cd /opt/hound
sudo -u hound docker-compose down -v
```

2. Backup current data if possible:
```bash
sudo cp /var/lib/docker/volumes/hound_hound-data/_data/hound.db ~/hound-backup.db
```

3. Restart containers:
```bash
sudo -u hound docker-compose up -d
```

4. Reconfigure from management interface

### Reinstall from Scratch

1. Stop and remove everything:
```bash
cd /opt/hound
sudo -u hound docker-compose down -v
sudo systemctl stop hound hound-kiosk
```

2. Remove installation:
```bash
sudo rm -rf /opt/hound
```

3. Re-run installation script

## Getting Help

If issues persist:

1. Check logs:
```bash
sudo -u hound docker-compose logs > hound-logs.txt
```

2. Collect system information:
```bash
uname -a > system-info.txt
docker version >> system-info.txt
docker-compose version >> system-info.txt
```

3. Review documentation in `/opt/hound/docs`

4. Check GitHub issues for similar problems
