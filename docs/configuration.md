# Hound Configuration Guide

This guide covers configuring Hound after installation.

## Initial Setup

### 1. Create Management Credential

On first access to the management interface, you'll be prompted to create a credential.

1. Open `http://<device-ip>:3000/management` in a browser
2. Follow the setup wizard to create a password or PIN
3. Store this credential securely

### 2. Configure Weather Location

1. Access management interface → Weather
2. Search for your location by name
3. Select from the results
4. The latitude and longitude will be saved automatically

### 3. Add Bus Stops

1. Access management interface → Bus Stops
2. Add bus stops using ATCO codes
3. Add custom labels (e.g., "School bus", "Town centre")
4. Enable/disable stops as needed
5. Adjust display order

### 4. Create Calendar Events

1. Access management interface → Calendar
2. Create events with:
   - Title
   - Date and time
   - All-day option
   - Category
   - Recurrence settings
   - Notes

### 5. Upload Photos

1. Access management interface → Photos
2. Upload family photos
3. Photos will display in the screensaver

## Environment Variables

Edit `/opt/hound/.env` to configure:

### Security

- `HOUND_SECRET_KEY`: Secret key for session signing (generate a secure random string)
- Change this to a unique value for each installation

### Timezone

- `HOUND_TIMEZONE`: Device timezone (default: `Europe/London`)
- Use IANA timezone format (e.g., `America/New_York`, `Asia/Tokyo`)

### Weather

- `HOUND_WEATHER_REFRESH_INTERVAL`: Weather refresh interval in seconds (default: 900 = 15 minutes)
- Recommended: 900-1800 seconds

### Bus

- `HOUND_BUS_REFRESH_INTERVAL`: Bus departure refresh interval in seconds (default: 60 = 1 minute)
- Recommended: 60-120 seconds

### Screensaver

- `HOUND_SCREENSAVER_TIMEOUT`: Inactivity timeout before screensaver starts (default: 60 seconds)
- `HOUND_PHOTO_ROTATION_INTERVAL`: Photo rotation interval in seconds (default: 10 seconds)
- `HOUND_DIMMING_START`: Dimming start time (default: 22:00)
- `HOUND_DIMMING_END`: Dimming end time (default: 07:00)

### Theme

- `HOUND_DAY_THEME_START`: Day theme start time (default: 07:00)
- `HOUND_EVENING_THEME_START`: Evening theme start time (default: 19:00)

### Backups

- `HOUND_BACKUP_SCHEDULE`: Backup schedule in cron format (default: `0 2 * * *` = 2 AM daily)
- `HOUND_BACKUP_RETENTION_DAYS`: Backup retention period (default: 30 days)

### Updates

- `HOUND_UPDATE_CHANNEL`: Update channel (`stable` or `beta`)
- `HOUND_AUTO_UPDATE_ENABLED`: Enable automatic updates (default: `true`)
- `HOUND_UPDATE_CHECK_INTERVAL`: Update check interval in seconds (default: 86400 = 24 hours)

## Management Interface Settings

### General Settings

Access via management interface → Settings

- Household timezone
- Date and clock preferences
- Theme transition times
- Refresh intervals
- Screensaver settings

### Event Categories

Access via management interface → Categories

Default categories:
- Bins and recycling
- Family
- Birthdays
- Appointments
- School and activities
- General

Customize:
- Category names
- Colours
- Descriptions

### Reminder Settings

Access via management interface → Reminders

- Configure reminder times for events
- Mark reminders as completed
- View upcoming reminders

## Database Settings

Hound uses SQLite with the following configuration:

- Location: `/data/hound.db` (Docker volume)
- Mode: WAL (Write-Ahead Logging)
- Journal mode: Normal
- Foreign keys: Enabled

No manual database configuration is typically required.

## Advanced Configuration

### Custom CSS

To customize the dashboard appearance:

1. Edit `frontend/src/index.css`
2. Rebuild the frontend:
```bash
cd /opt/hound/frontend
npm run build
sudo -u hound docker-compose up -d --build frontend
```

### API Base URL

The frontend API base URL is configured via:
- Environment variable: `VITE_API_BASE_URL`
- Default: `http://backend:8000` (internal Docker network)

For external access, configure nginx reverse proxy.

### Storage Locations

- Database: `/data/hound.db` (Docker volume)
- Photos: `/data/photos` (Docker volume)
- Backups: `/data/backups` (Docker volume)

These persist across container restarts.

## Troubleshooting Configuration

### Weather Not Updating

1. Check weather location is configured
2. Verify network connectivity
3. Check refresh interval in `.env`
4. View system status in management interface

### Bus Data Not Updating

1. Verify ATCO codes are correct
2. Check bustimes.org API status
3. Review bus refresh interval
4. Check system status for errors

### Screensaver Not Activating

1. Verify inactivity timeout setting
2. Check photos are uploaded
3. Test by waiting without interaction
4. Check browser console for errors

### Theme Not Changing

1. Verify theme transition times
2. Check timezone is correct
3. Wait for automatic transition or restart

### Backups Not Running

1. Check backup schedule format
2. Verify backup directory permissions
3. Check system status for errors
4. Test manual backup from management interface
