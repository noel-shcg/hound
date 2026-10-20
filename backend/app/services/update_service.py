import subprocess
import os
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import shutil


class UpdateService:
    """Service for managing automatic software updates."""
    
    def __init__(self, repo_path: str = "/opt/hound"):
        self.repo_path = Path(repo_path)
        self.update_log_path = self.repo_path / "logs" / "updates.log"
        self.update_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _log(self, message: str):
        """Log update operations."""
        timestamp = datetime.utcnow().isoformat()
        log_line = f"[{timestamp}] {message}\n"
        with open(self.update_log_path, "a") as f:
            f.write(log_line)
        print(log_line.strip())
    
    def check_for_updates(self) -> Dict[str, any]:
        """Check if updates are available."""
        try:
            self._log("Checking for updates...")
            
            # Fetch latest from remote
            result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self._log(f"Git fetch failed: {result.stderr}")
                return {"available": False, "error": result.stderr}
            
            # Check if local is behind remote
            result = subprocess.run(
                ["git", "rev-list", "--count", "--left-right", "HEAD...origin/main"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self._log(f"Git rev-list failed: {result.stderr}")
                return {"available": False, "error": result.stderr}
            
            # Output format: "behind_count\tahead_count"
            parts = result.stdout.strip().split("\t")
            if len(parts) == 2:
                behind = int(parts[0])
                ahead = int(parts[1])
                
                if behind > 0:
                    self._log(f"Updates available: {behind} commits behind")
                    return {
                        "available": True,
                        "behind": behind,
                        "ahead": ahead,
                        "current_head": self._get_current_commit(),
                        "latest_head": self._get_latest_commit()
                    }
                else:
                    self._log("Already up to date")
                    return {"available": False, "behind": 0, "ahead": ahead}
            
            return {"available": False, "error": "Unexpected git output"}
        
        except Exception as e:
            self._log(f"Error checking for updates: {str(e)}")
            return {"available": False, "error": str(e)}
    
    def _get_current_commit(self) -> str:
        """Get current commit hash."""
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    
    def _get_latest_commit(self) -> str:
        """Get latest commit hash from origin."""
        result = subprocess.run(
            ["git", "rev-parse", "origin/main"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    
    def create_backup(self) -> Optional[str]:
        """Create a backup before updating."""
        try:
            self._log("Creating pre-update backup...")
            
            # Create backup archive directly
            from app.core.config import settings
            import tarfile
            from datetime import datetime
            
            backup_dir = Path(settings.backup_dir)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"hound_pre_update_{timestamp}.tar.gz"
            file_path = backup_dir / filename
            
            with tarfile.open(file_path, "w:gz") as tar:
                db_path = Path(settings.database_path)
                if db_path.exists():
                    tar.add(db_path, arcname="hound.db")
                
                photo_dir = Path(settings.photo_dir)
                if photo_dir.exists():
                    tar.add(photo_dir, arcname="photos")
            
            self._log(f"Backup created: {filename}")
            return str(file_path)
        
        except Exception as e:
            self._log(f"Error creating backup: {str(e)}")
            return None
    
    def apply_update(self) -> Dict[str, any]:
        """Apply available updates."""
        try:
            self._log("Starting update process...")
            
            # Create backup
            backup_path = self.create_backup()
            if not backup_path:
                return {"success": False, "error": "Failed to create backup"}
            
            # Pull latest changes
            self._log("Pulling latest changes...")
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self._log(f"Git pull failed: {result.stderr}")
                return {"success": False, "error": result.stderr, "backup": backup_path}
            
            self._log("Changes pulled successfully")
            
            # Rebuild and restart containers
            self._log("Rebuilding Docker containers...")
            result = subprocess.run(
                ["docker-compose", "up", "-d", "--build"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self._log(f"Docker rebuild failed: {result.stderr}")
                return {"success": False, "error": result.stderr, "backup": backup_path}
            
            self._log("Docker containers rebuilt and restarted")
            
            # Health check
            self._log("Running health check...")
            import time
            time.sleep(10)  # Wait for services to start
            
            result = subprocess.run(
                ["curl", "-f", "http://localhost:3000/health"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self._log("Health check failed, rolling back...")
                self._rollback(backup_path)
                return {"success": False, "error": "Health check failed", "backup": backup_path}
            
            self._log("Update completed successfully")
            return {
                "success": True,
                "backup": backup_path,
                "new_commit": self._get_current_commit()
            }
        
        except Exception as e:
            self._log(f"Error applying update: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _rollback(self, backup_path: str):
        """Rollback to previous version using backup."""
        try:
            self._log("Rolling back...")
            
            # Restore from backup archive
            from app.core.config import settings
            import tarfile
            
            backup_file = Path(backup_path)
            if not backup_file.exists():
                self._log(f"Backup file not found: {backup_path}")
                return
            
            # Extract backup
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(path=Path(settings.backup_dir).parent)
            
            self._log("Backup restored")
            
            # Reset git to previous commit
            result = subprocess.run(
                ["git", "reset", "--hard", "HEAD@{1}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self._log("Git rollback successful")
                # Rebuild containers
                subprocess.run(
                    ["docker-compose", "up", "-d", "--build"],
                    cwd=self.repo_path,
                    capture_output=True
                )
        
        except Exception as e:
            self._log(f"Error during rollback: {str(e)}")
    
    def get_update_status(self) -> Dict[str, any]:
        """Get current update status."""
        return {
            "last_check": datetime.utcnow().isoformat(),
            "current_commit": self._get_current_commit(),
            "latest_commit": self._get_latest_commit(),
            "update_available": self.check_for_updates().get("available", False)
        }


# Singleton instance
update_service = UpdateService()
