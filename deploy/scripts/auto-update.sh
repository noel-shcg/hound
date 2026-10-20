#!/bin/bash
# Hound Auto-Update Script
# This script checks for and applies updates to Hound

set -e

INSTALL_DIR="/opt/hound"
LOG_FILE="/var/log/hound-auto-update.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Starting auto-update check..."

cd "$INSTALL_DIR" || exit 1

# Check if git repository exists
if [ ! -d ".git" ]; then
    log "Not a git repository, skipping update"
    exit 0
fi

# Fetch latest
log "Fetching latest changes..."
git fetch origin

# Check if updates are available
BEHIND=$(git rev-list --count --left-right HEAD...origin/main | awk '{print $1}')

if [ "$BEHIND" -eq "0" ]; then
    log "Already up to date"
    exit 0
fi

log "Updates available: $BEHIND commits behind"

# Create backup
log "Creating backup..."
BACKUP_FILE="/var/lib/docker/volumes/hound_hound-data/_data/backups/pre-update-$(date +%Y%m%d_%H%M%S).tar.gz"
mkdir -p "$(dirname "$BACKUP_FILE")"

# Backup database and photos
tar -czf "$BACKUP_FILE" -C /var/lib/docker/volumes/hound_hound-data/_data hound.db photos 2>/dev/null || true

if [ -f "$BACKUP_FILE" ]; then
    log "Backup created: $BACKUP_FILE"
else
    log "Backup failed, aborting update"
    exit 1
fi

# Pull latest changes
log "Pulling latest changes..."
git pull origin main

# Rebuild and restart containers
log "Rebuilding Docker containers..."
docker-compose up -d --build

# Wait for services to start
log "Waiting for services to start..."
sleep 30

# Health check
log "Running health check..."
if curl -f http://localhost:3000/health > /dev/null 2>&1; then
    log "Health check passed"
    log "Update completed successfully"
else
    log "Health check failed, rolling back..."
    
    # Rollback git
    git reset --hard HEAD@{1}
    
    # Rebuild containers
    docker-compose up -d --build
    
    log "Rollback completed"
    exit 1
fi
