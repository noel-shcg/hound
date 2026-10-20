# Hound

![Hound](https://img.shields.io/badge/Household-Dashboard-blue)
![Version](https://img.shields.io/badge/version-0.1.0-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![React](https://img.shields.io/badge/react-19+-blue)
![License](https://img.shields.io/badge/license-MIT-orange)

Hound is a self-hosted household dashboard application designed to run on a Linux touchscreen device in a central location in a family home. It provides an attractive, always-available household information display with a separate web management interface for configuring the system.

## Features

![Dashboard](https://img.shields.io/badge/Dashboard-Touch--friendly-purple)
![Weather](https://img.shields.io/badge/Weather-Open--Meteo-yellow)
![Bus](https://img.shields.io/badge/Bus-Bustimes.org-red)
![Calendar](https://img.shields.io/badge/Calendar-Recurring-green)
![Screensaver](https://img.shields.io/badge/Screensaver-Photo--slideshow-orange)

- **Dashboard**: Full-screen, touch-friendly display showing:
  - Time and date (UK locale, 24-hour clock)
  - Current weather and forecast (via Open-Meteo)
  - Upcoming bus departures (via Bustimes.org)
  - Household calendar with month view and seven-day agenda
  - Event categories with custom colours
  - Flexible recurring events
  - Dashboard reminders
  - Family-photo screensaver with overnight dimming

- **Management Interface**: Password-protected web application for:
  - Configuring weather location
  - Managing bus stops with custom labels
  - Creating and managing events and recurring schedules
  - Configuring event categories and colours
  - Uploading and managing family photos
  - Configuring screensaver settings
  - Managing reminders
  - Automated backups and manual export/import
  - System status and diagnostics
  - Automatic update management
  - Security settings

- **Operational Features**:
  - Automatic day/evening theme switching
  - Offline capability for local features
  - Robust error handling and stale-data indicators
  - Automatic scheduled backups
  - Automatic software updates with health checks
  - Linux kiosk mode for always-on display

## Architecture

Hound consists of:

- **Frontend**: React + TypeScript with Vite
- **Backend**: FastAPI with SQLAlchemy
- **Database**: SQLite with Alembic migrations
- **Deployment**: Docker Compose

The application is designed to run entirely on a modest Linux touchscreen computer. The dashboard and management interface share the same backend services and database.

## Technology Stack

![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![SQLite](https://img.shields.io/badge/SQLite-3+-red)

- **Frontend**: React, TypeScript, Vite
- **Backend**: Python, FastAPI, Pydantic, SQLAlchemy, Alembic
- **Database**: SQLite (persistent volume)
- **External APIs**: Open-Meteo (weather), Bustimes.org (bus times)
- **Deployment**: Docker Compose

## Prerequisites

- Docker and Docker Compose
- Linux touchscreen device (1920×1080 landscape recommended)
- Home network access for management interface

## Repository Structure

```
Hound/
├── frontend/          # React + TypeScript dashboard and management UI
├── backend/           # FastAPI backend with SQLAlchemy
├── deploy/            # Kiosk and systemd configuration
├── docs/              # Documentation
├── docker-compose.yml # Docker Compose configuration
├── .env.example       # Environment variables template
└── README.md          # This file
```

## Quick Start

### 1. Clone and Configure

```bash
# Clone the repository
git clone <repository-url>
cd Hound

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Set initial secure credentials and preferences
```

### 2. Start the Application

```bash
# Build and start with Docker Compose
docker-compose up -d

# Wait for services to start (check with docker-compose ps)
```

### 3. Access the Dashboard

- **Dashboard**: Open `http://localhost:3000` on the touchscreen device
- **Management**: Open `http://localhost:3000/management` on any device on your home network

### 4. Initial Setup

1. Create your household credential (PIN or password) on first management access
2. Configure your weather location via the management interface
3. Add bus stops with ATCO codes and custom labels
4. Create calendar events and recurring schedules
5. Upload family photos for the screensaver
6. Configure automatic backups in settings

## Development Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Build production assets
npm run build
```

## Production Deployment

### Docker Compose

```bash
# Build and start in production mode
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Kiosk Mode

For automatic full-screen display on a Linux touchscreen device, see `docs/deployment.md` for systemd service configuration and browser kiosk setup.

## Configuration

Key environment variables (see `.env.example`):

- `HOUND_SECRET_KEY`: Secret key for session signing
- `HOUND_DATABASE_PATH`: Path to SQLite database
- `HOUND_PHOTO_DIR`: Directory for uploaded photos
- `HOUND_BACKUP_DIR`: Directory for backups
- `HOUND_TIMEZONE`: Device timezone (default: Europe/London)
- `HOUND_WEATHER_REFRESH_INTERVAL`: Weather refresh interval in seconds
- `HOUND_BUS_REFRESH_INTERVAL`: Bus refresh interval in seconds
- `HOUND_SCREENSAVER_TIMEOUT`: Screensaver inactivity timeout in seconds
- `HOUND_PHOTO_ROTATION_INTERVAL`: Photo rotation interval in seconds

## Backup and Restore

### Automatic Backups

Hound automatically creates scheduled backups of the database and uploaded photos. Configure the schedule and retention policy in the management interface.

### Manual Export

From the management interface, export a portable backup archive containing all household data.

### Restore

Use the management interface to restore from a backup archive. The restore process validates the archive and creates a safety backup before applying changes.

**Important**: Backups stored only on the touchscreen device do not protect against physical storage failure. Copy backups to external storage regularly.

## Troubleshooting

See `docs/troubleshooting.md` for common issues and recovery procedures.

Key troubleshooting steps:

- Check container status: `docker-compose ps`
- View logs: `docker-compose logs backend` or `docker-compose logs frontend`
- Verify database file exists and is accessible
- Check network connectivity for external APIs
- Review system status in the management interface

## Security

- Management interface requires authentication
- Credentials are hashed using bcrypt
- No default password is shipped
- LAN-only access by default
- All input is validated on the backend
- File uploads are validated and sandboxed
- No external authentication services or cloud accounts

## Update Management

Hound supports automatic software updates with health checks and rollback capability. Configure update channels and schedules in the management interface. Updates are applied only after verification and pre-update backup.

## Limitations

- No WhatsApp or messaging integration
- No cloud accounts or remote access
- No physical backlight control (dimming is software-based)
- LAN-only by default (no public internet exposure)
- Single-device deployment (not designed for multi-server setups)

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
