from pathlib import Path
from app.config import settings

def _flag_dir() -> Path:
    path = settings.data_dir / "unread_changes"
    path.mkdir(parents=True, exist_ok=True)
    return path

def _flag_path(site_id: int) -> Path:
    return _flag_dir() / f"site-{site_id}.flag"

def mark_unread(site_id: int) -> None:
    _flag_path(site_id).write_text("unread\n", encoding="utf-8")

def clear_unread(site_id: int) -> None:
    _flag_path(site_id).unlink(missing_ok=True)

def has_unread(site_id: int) -> bool:
    return _flag_path(site_id).exists()
