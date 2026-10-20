# Hound Backup and Restore Guide

This guide covers backup and restore procedures for Hound.

## Overview

Hound includes automatic scheduled backups and manual backup/restore functionality. Backups include:

- SQLite database (events, settings, credentials, etc.)
- Uploaded family photos
- Application configuration

## Automatic Backups

### Configuration

Automatic backups are configured via environment variables in `/opt/hound/.env`:

```bash
HOUND_BACKUP_SCHEDULE="0 2 * * *"  # Daily at 2 AM
HOUND_BACKUP_RETENTION_DAYS=30      # Keep backups for 30 days
```

### Backup Schedule Format

The schedule uses cron format:
- `* * * * *` = Every minute
- `0 * * * *` = Every hour
- `0 2 * * *` = Daily at 2 AM
- `0 2 * * 0` = Weekly on Sunday at 2 AM
- `0 2 1 * *` = Monthly on the 1st at 2 AM

### Retention Policy

Old backups are automatically deleted based on `HOUND_BACKUP_RETENTION_DAYS`. Ensure you have sufficient storage.

### Monitoring

Check backup status:
- Access management interface → System Status
- Look for "backup" component status
- View last successful backup time

## Manual Backup

### Via Management Interface

1. Access management interface → Backups
2. Click "Create Backup"
3. Wait for completion
4. Download the backup file

### Via Command Line

```bash
cd /opt/hound
sudo -u hound docker-compose exec backend python -c "
import asyncio
from app.api.backups import create_backup
from app.core.database import SessionLocal
db = SessionLocal()
result = asyncio.run(create_backup(db))
print(f'Backup created: {result.filename}')
"
```

## Backup File Format

Backups are tar.gz archives containing:

```
hound_backup_YYYYMMDD_HHMMSS.tar.gz
├── hound.db              # SQLite database
└── photos/               # Uploaded photos
    ├── photo1.jpg
    ├── photo2.png
    └── ...
```

A manifest file is stored in the database with:
- Backup version
- Creation timestamp
- File size
- Success/failure status

## Restore

### Prerequisites

- Valid backup archive
- Sufficient disk space
- Application stopped (recommended)

### Via Management Interface

1. Access management interface → Backups
2. Select a backup from the list
3. Click "Restore"
4. Confirm the restore action
5. Wait for completion

A safety backup of the current state is created automatically before restore.

### Via Command Line

```bash
cd /opt/hound
sudo -u hound docker-compose exec backend python -c "
import asyncio
from app.api.backups import restore_backup
from app.core.database import SessionLocal
db = SessionLocal()
result = asyncio.run(restore_backup(db, backup_id=<ID>))
print(f'Restore completed: {result}')
"
```

### Manual Restore

If the automated restore fails:

1. Stop containers:
```bash
cd /opt/hound
sudo -u hound docker-compose down
```

2. Extract backup:
```bash
cd /tmp
tar -xzf /path/to/backup.tar.gz
```

3. Copy to data volume:
```bash
sudo cp hound.db /var/lib/docker/volumes/hound_hound-data/_data/
sudo cp -r photos /var/lib/docker/volumes/hound_hound-data/_data/
sudo chown -R hound:hound /var/lib/docker/volumes/hound_hound-data/_data/
```

4. Start containers:
```bash
cd /opt/hound
sudo -u hound docker-compose up -d
```

## Backup Location

Backups are stored in:
- Docker volume: `hound_hound-data/_data/backups`
- Host path: `/var/lib/docker/volumes/hound_hound-data/_data/backups`

List backups:
```bash
sudo -u hound ls -lh /var/lib/docker/volumes/hound_hound-data/_data/backups/
```

## Off-Device Backup

**Important**: Backups stored only on the touchscreen device do not protect against physical theft or device failure.

### Copy to External Storage

1. Copy backup files to USB drive:
```bash
sudo cp /var/lib/docker/volumes/hound_hound-data/_data/backups/*.tar.gz /media/usb/
```

2. Or use SCP:
```bash
scp user@hound-device:/var/lib/docker/volumes/hound_hound-data/_data/backups/*.tar.gz ./
```

3. Or use rsync:
```bash
rsync -av user@hound-device:/var/lib/docker/volumes/hound_hound-data/_data/backups/ ./backups/
```

### Cloud Backup (Optional)

Set up automated backup to cloud storage:

```bash
# Using rclone
rclone copy /var/lib/docker/volumes/hound_hound-data/_data/backups/ remote:hound-backups

# Using AWS S3
aws s3 sync /var/lib/docker/volumes/hound_hound-data/_data/backups/ s3://bucket-name/hound-backups
```

## Backup Verification

### Check Backup Integrity

```bash
# Test tar.gz integrity
tar -tzf /path/to/backup.tar.gz > /dev/null
echo $?  # Should be 0

# Extract and verify database
tar -xzf /path/to/backup.tar.gz
sqlite3 hound.db "PRAGMA integrity_check;"
```

### Test Restore on Test System

Before restoring on production:
1. Set up a test Hound instance
2. Restore the backup on the test system
3. Verify all data is present
4. Test calendar, photos, settings

## Disaster Recovery

### Device Failure

If the touchscreen device fails completely:

1. Recover backups from external storage
2. Set up new device
3. Install Hound
4. Restore from backup

### Database Corruption

If the database becomes corrupted:

1. Stop containers:
```bash
cd /opt/hound
sudo -u hound docker-compose down
```

2. Check database integrity:
```bash
sudo -u hound docker-compose run --rm backend sqlite3 /data/hound.db "PRAGMA integrity_check;"
```

3. If corrupted, restore from most recent backup

### Photo Loss

If photos are accidentally deleted:

1. Restore from backup
2. Or restore only photos:
```bash
tar -xzf backup.tar.gz photos/
sudo cp -r photos/* /var/lib/docker/volumes/hound_hound-data/_data/photos/
```

## Best Practices

1. **Regular Off-Device Backups**: Copy backups to external storage weekly
2. **Test Restores**: Periodically test restore procedure on a test system
3. **Monitor Storage**: Ensure sufficient disk space for backups
4. **Retention Policy**: Adjust retention based on storage capacity
5. **Version Compatibility**: Keep backups compatible with application version
6. **Secure Storage**: Encrypt backups if they contain sensitive data
7. **Documentation**: Document your backup procedures and locations

## Troubleshooting

### Backup Fails

1. Check disk space:
```bash
df -h
```

2. Check backup directory permissions:
```bash
ls -la /var/lib/docker/volumes/hound_hound-data/_data/backups
```

3. View error in system status:
   - Management interface → System Status

4. Check backend logs:
```bash
sudo -u hound docker-compose logs backend
```

### Restore Fails

1. Verify backup file integrity
2. Check disk space
3. Ensure application is stopped
4. Review error message
5. Check safety backup was created

### Backup Size Too Large

1. Check photo sizes:
```bash
sudo -u hound du -sh /var/lib/docker/volumes/hound_hound-data/_data/photos/*
```

2. Optimize large photos
3. Consider photo cleanup
4. Adjust retention policy

## Automation Scripts

### Daily Backup Script

Create `/opt/hound/scripts/daily-backup.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/lib/docker/volumes/hound_hound-data/_data/backups"
EXTERNAL_DIR="/media/external/backups"

# Create backup
cd /opt/hound
sudo -u hound docker-compose exec -T backend python -c "
import asyncio
from app.api.backups import create_backup
from app.core.database import SessionLocal
db = SessionLocal()
result = asyncio.run(create_backup(db))
print(result.filename)
" > /tmp/backup-filename.txt

BACKUP_FILE=$(cat /tmp/backup-filename.txt)

# Copy to external storage
if [ -d "$EXTERNAL_DIR" ]; then
    cp "$BACKUP_DIR/$BACKUP_FILE" "$EXTERNAL_DIR/"
fi

# Clean old backups (older than 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

Add to crontab:
```bash
sudo crontab -e
# Add: 0 2 * * * /opt/hound/scripts/daily-backup.sh
```
