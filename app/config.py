import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://webmonitor:devpassword@postgres:5432/webmonitor")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    data_dir: Path = Path(os.getenv("DATA_DIR", "/app/data"))
    app_secret: str = os.getenv("APP_SECRET", "change-me")
    admin_user: str = os.getenv("ADMIN_USER", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")

    @property
    def screenshot_dir(self):
        p = self.data_dir / "screenshots"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def diff_dir(self):
        p = self.data_dir / "diffs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def backup_dir(self):
        p = self.data_dir / "backups"
        p.mkdir(parents=True, exist_ok=True)
        return p

settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
