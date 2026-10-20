from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    secret_key: str = "change-this-in-production"
    database_path: str = "/data/hound.db"
    photo_dir: str = "/data/photos"
    backup_dir: str = "/data/backups"
    timezone: str = "Europe/London"
    
    weather_refresh_interval: int = 900
    bus_refresh_interval: int = 60
    
    screensaver_timeout: int = 60
    photo_rotation_interval: int = 10
    dimming_start: str = "22:00"
    dimming_end: str = "07:00"
    
    day_theme_start: str = "07:00"
    evening_theme_start: str = "19:00"
    
    backup_schedule: str = "0 2 * * *"
    backup_retention_days: int = 30
    
    update_channel: str = "stable"
    auto_update_enabled: bool = True
    update_check_interval: int = 86400
    
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    class Config:
        env_prefix = "HOUND_"
        extra = "ignore"


settings = Settings()
