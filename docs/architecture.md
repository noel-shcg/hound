# Hound Architecture

This document describes the architecture of Hound.

## High-Level Architecture

Hound is a modular household dashboard application with the following components:

- **Frontend**: React + TypeScript dashboard and management interface
- **Backend**: FastAPI REST API with business logic
- **Database**: SQLite with Alembic migrations
- **Services**: External API integrations (weather, bus)
- **Jobs**: Scheduled background tasks
- **Deployment**: Docker Compose

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
│  ┌──────────────┐         ┌──────────────────────────┐    │
│  │  Dashboard   │         │  Management Interface   │    │
│  │  (Read-only) │         │  (Authenticated)        │    │
│  └──────┬───────┘         └───────────┬──────────────┘    │
│         │                               │                   │
│         └───────────────┬───────────────┘                   │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │ HTTP/JSON
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                    Nginx (Frontend)                          │
│                  Static file serving                         │
│                  API proxy (→ backend)                       │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                 FastAPI Backend                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Layer                                            │  │
│  │  - Authentication                                     │  │
│  │  - Input validation                                   │  │
│  │  - Response formatting                                │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Services                                             │  │
│  │  - Weather Service (Open-Meteo)                       │  │
│  │  - Bus Service (Bustimes.org)                         │  │
│  │  - Recurrence Service                                 │  │
│  │  - Reminder Service                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Background Jobs (APScheduler)                        │  │
│  │  - Weather refresh                                    │  │
│  │  - Bus departure refresh                              │  │
│  │  - Reminder evaluation                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                 SQLite Database                             │
│  - Events                                              │
│  - Categories                                          │
│  - Bus stops                                           │
│  - Weather location                                     │
│  - Photos                                              │
│  - Settings                                            │
│  - Credentials                                         │
│  - Backups                                             │
│  - System status                                       │
└─────────────────────────────────────────────────────────────┘

External APIs:
- Open-Meteo (weather)
- Bustimes.org (bus departures)
```

## Frontend Architecture

### Directory Structure

```
frontend/
├── src/
│   ├── api/              # API client and typed interfaces
│   │   ├── client.ts    # Axios configuration
│   │   ├── auth.ts      # Authentication API
│   │   ├── weather.ts   # Weather API
│   │   ├── bus.ts       # Bus API
│   │   ├── events.ts    # Events API
│   │   ├── categories.ts # Categories API
│   │   └── photos.ts    # Photos API
│   ├── components/       # Reusable components
│   │   ├── Clock.tsx
│   │   ├── WeatherDisplay.tsx
│   │   ├── BusDisplay.tsx
│   │   └── Screensaver.tsx
│   ├── dashboard/       # Dashboard-specific components
│   │   ├── Dashboard.tsx # Main dashboard layout
│   │   ├── Calendar.tsx
│   │   └── Agenda.tsx
│   ├── management/      # Management interface (to be implemented)
│   ├── hooks/           # Custom React hooks
│   │   └── useTheme.ts
│   ├── styles/          # Design tokens and styling
│   │   └── design-tokens.ts
│   ├── App.tsx          # Main app with routing
│   └── index.css        # Global styles
├── public/              # Static assets
├── Dockerfile           # Production build
├── nginx.conf           # Nginx configuration
└── vite.config.ts       # Vite configuration
```

### Key Patterns

- **API Client**: Centralized Axios instance with auth token handling
- **Type Safety**: TypeScript interfaces for all API responses
- **Theme System**: CSS custom properties for day/evening themes
- **Component Composition**: Reusable UI components
- **Error Handling**: Global error interceptor for auth failures

## Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── auth.py       # Authentication
│   │   ├── settings.py   # Settings management
│   │   ├── bus_stops.py  # Bus stop CRUD
│   │   ├── weather.py    # Weather location and data
│   │   ├── events.py     # Event CRUD
│   │   ├── categories.py # Category CRUD
│   │   ├── reminders.py  # Reminder management
│   │   ├── photos.py     # Photo upload/management
│   │   ├── backups.py    # Backup/restore
│   │   ├── system.py     # System status and health
│   │   └── dashboard.py  # Dashboard aggregated data
│   ├── core/             # Core functionality
│   │   ├── config.py     # Settings from environment
│   │   ├── database.py   # SQLAlchemy setup
│   │   └── security.py   # Authentication and authorization
│   ├── models/           # SQLAlchemy models
│   │   ├── settings.py
│   │   ├── credential.py
│   │   ├── bus_stop.py
│   │   ├── weather_location.py
│   │   ├── event_category.py
│   │   ├── event.py
│   │   ├── reminder.py
│   │   ├── photo.py
│   │   ├── backup.py
│   │   └── system_status.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── settings.py
│   │   ├── credential.py
│   │   ├── bus_stop.py
│   │   ├── weather.py
│   │   ├── event.py
│   │   ├── category.py
│   │   ├── reminder.py
│   │   ├── photo.py
│   │   ├── backup.py
│   │   └── system.py
│   ├── services/         # Business logic
│   │   ├── weather_service.py
│   │   ├── bus_service.py
│   │   ├── recurrence_service.py
│   │   └── reminder_service.py
│   ├── jobs/             # Background jobs
│   │   └── scheduler.py
│   └── main.py           # FastAPI application
├── migrations/           # Alembic migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/                # Tests
├── Dockerfile
├── alembic.ini
└── pyproject.toml
```

### Key Patterns

- **Dependency Injection**: FastAPI Depends for database sessions
- **Service Layer**: Business logic separated from API layer
- **Singleton Services**: Single instances for external API clients
- **Schema Validation**: Pydantic for request/response validation
- **Background Jobs**: APScheduler for scheduled tasks
- **Error Handling**: Global exception handlers

## Database Schema

### Entities

- **settings**: Key-value configuration
- **credentials**: Authentication credentials (hashed)
- **bus_stops**: Configured bus stops
- **weather_locations**: Weather location configuration
- **event_categories**: Event categories with colours
- **events**: Calendar events
- **recurrence_rules**: Recurrence patterns for events
- **reminders**: Event reminders
- **photos**: Uploaded family photos
- **backups**: Backup records
- **system_status**: Component health status

### Relationships

- Event → Category (many-to-one)
- Event → RecurrenceRule (one-to-one)
- Event → Reminder (one-to-many)
- Reminder → Event (many-to-one)

### Indexes

- Events: start_datetime (for date range queries)
- Bus stops: atco_code (unique), enabled
- Weather locations: (single record)
- Credentials: (single record)
- Photos: filename (unique)

## External Integrations

### Weather Service (Open-Meteo)

- **API**: `https://api.open-meteo.com/v1`
- **Features**: Current weather, forecast, geocoding
- **Caching**: In-memory cache with configurable TTL
- **Error Handling**: Fallback to cached data on failure
- **Rate Limiting**: Respects API limits via refresh interval

### Bus Service (Bustimes.org)

- **API**: `https://bustimes.org/stops/{ATCO_CODE}/times.json`
- **Features**: Real-time departures
- **Caching**: In-memory cache with 1-minute TTL
- **Error Handling**: Fallback to cached data on failure
- **Rate Limiting**: 1-minute refresh interval

## Authentication

### Flow

1. User accesses `/management/login`
2. Enters password
3. Frontend sends POST to `/api/auth/login`
4. Backend verifies password hash
5. Backend returns JWT access token
6. Frontend stores token in localStorage
7. Frontend includes token in Authorization header
8. Backend validates token on protected endpoints

### Security

- Passwords hashed with bcrypt
- JWT tokens with 24-hour expiry
- Login throttling (5 attempts = 15-minute lockout)
- CSRF protection (same-origin)
- LAN-only binding by default

## Background Jobs

### Scheduler

- **Framework**: APScheduler
- **Trigger**: Interval-based
- **Concurrency**: AsyncIO
- **Persistence**: In-memory (restart clears jobs)

### Jobs

1. **Weather Refresh**
   - Interval: 15 minutes (configurable)
   - Action: Fetch current weather from Open-Meteo
   - Caching: Update in-memory cache
   - Status: Update system status

2. **Bus Refresh**
   - Interval: 1 minute (configurable)
   - Action: Fetch departures for all enabled stops
   - Caching: Update in-memory cache per stop
   - Status: Update system status

3. **Reminder Evaluation**
   - Interval: 1 hour
   - Action: Generate reminders for recurring events
   - Persistence: Create reminder records in database

## Deployment Architecture

### Docker Compose

- **Frontend Service**: Nginx serving static React build
- **Backend Service**: FastAPI with uvicorn
- **Volumes**: Persistent data (database, photos, backups)
- **Networks**: Bridge network for service communication
- **Health Checks**: HTTP endpoint monitoring

### Kiosk Mode

- **Systemd Service**: User-level service for kiosk browser
- **Browser**: Firefox in kiosk mode (full-screen, no chrome)
- **Auto-start**: Depends on display manager auto-login
- **Crash Recovery**: Systemd restart policy

## Data Flow

### Dashboard Load

1. Frontend loads → fetches dashboard summary
2. Backend aggregates data from:
   - Events (next 7 days)
   - Bus stops (enabled)
   - Weather location
3. Frontend renders components
4. Components fetch specific data via API
5. Services return cached or fresh data
6. UI updates with new data

### Weather Update

1. Background job triggers
2. Weather service fetches from Open-Meteo
3. Response parsed and cached
4. System status updated
5. Frontend polls or receives update
6. UI refreshes with new data

### Event Creation

1. User submits event form
2. Frontend validates and sends to API
3. Backend validates with Pydantic
4. If recurring, recurrence rule created
5. Event saved to database
6. Reminders created if configured
7. Response returned to frontend
8. Frontend updates UI

## Error Handling Strategy

### Frontend

- Global error interceptor for API calls
- Component-level error boundaries
- Graceful degradation for missing data
- User-friendly error messages
- Retry logic for transient failures

### Backend

- Global exception handlers
- Input validation with Pydantic
- Database transaction rollback on error
- Logging of errors with context
- Fallback to cached data
- Status codes indicating error type

### External APIs

- Timeout handling
- Retry with exponential backoff
- Fallback to cached data
- Status tracking in system status
- Graceful degradation

## Performance Considerations

### Frontend

- Code splitting with React Router
- Lazy loading of management interface
- Image optimization for photos
- Debounced API calls
- Memoization of expensive computations

### Backend

- Database connection pooling
- Query optimization with indexes
- Caching of external API responses
- Async I/O for concurrent requests
- Pagination for large datasets

### Database

- WAL mode for better concurrency
- Appropriate indexes for common queries
- Connection timeout configuration
- Regular vacuum operations
- Backup with minimal downtime

## Security Architecture

### Network

- LAN-only binding by default
- No public internet exposure
- Firewall rules for additional protection
- No router port forwarding recommended

### Application

- Input validation on all endpoints
- SQL injection prevention (parameterized queries)
- XSS prevention (React escapes by default)
- CSRF protection (same-origin)
- Secure file upload handling

### Data

- Passwords hashed with bcrypt
- JWT tokens with expiration
- No secrets in logs
- Secure session handling
- Sensitive data not exposed in errors

## Scalability

### Current Design

- Single-device deployment
- SQLite database (no separate database server)
- In-memory caching
- No message queue
- No Redis

### Limitations

- Single user/household
- No horizontal scaling
- Limited concurrent users
- Single point of failure (device)

### Future Enhancements (Optional)

- PostgreSQL for multi-user support
- Redis for distributed caching
- Message queue for job processing
- Load balancing for multiple devices
- Cloud backup integration

## Monitoring

### Health Checks

- `/health`: Basic liveness
- `/api/system/health`: Comprehensive health
- Docker health checks for containers
- Systemd service monitoring

### Logging

- Structured logging with levels
- Component-specific loggers
- Error logging with context
- No sensitive data in logs
- Log rotation (Docker handles)

### Metrics

- System status in database
- Last successful update times
- Error counts per component
- API response times (basic)
- Storage capacity warnings

## Testing Strategy

### Backend Tests

- Unit tests for business logic
- Integration tests for API endpoints
- Tests for recurrence calculations
- Tests for external API parsing
- Database migration tests

### Frontend Tests

- Component rendering tests
- User interaction tests
- API integration tests
- Theme switching tests
- Screensaver activation tests

### Deployment Tests

- Docker build tests
- Container startup tests
- Health check tests
- Database migration tests
- End-to-end smoke tests
