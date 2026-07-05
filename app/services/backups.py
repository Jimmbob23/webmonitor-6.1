import csv
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from app.config import settings
from app.models import BackupEntry, Folder, Site
from app.services.monitor import normalize_url

BACKUP_COLUMNS = [
    "name","url","folder","tags_csv","schedule_type","interval_seconds",
    "cron_expression","threshold_percent","wait_seconds","viewport_width",
    "viewport_height","ignore_selectors","cookie_mode","enabled",
]

def _bool(value) -> bool:
    return str(value).strip().lower() in ("1","true","yes","ja","on")

def create_config_backup(db: Session) -> BackupEntry:
    filename = f"sites-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.csv"
    path = settings.backup_dir / filename
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=BACKUP_COLUMNS)
        writer.writeheader()
        for site in db.query(Site).order_by(Site.id).all():
            writer.writerow({
                "name": site.name,
                "url": site.url,
                "folder": site.folder.name if site.folder else "",
                "tags_csv": site.tags_csv,
                "schedule_type": site.schedule_type,
                "interval_seconds": site.interval_seconds,
                "cron_expression": site.cron_expression,
                "threshold_percent": site.threshold_percent,
                "wait_seconds": site.wait_seconds,
                "viewport_width": site.viewport_width,
                "viewport_height": site.viewport_height,
                "ignore_selectors": site.ignore_selectors,
                "cookie_mode": site.cookie_mode,
                "enabled": site.enabled,
            })
    entry = BackupEntry(filename=filename)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def restore_config_backup(db: Session, csv_path: Path, replace_existing: bool = False) -> int:
    restored = 0
    if replace_existing:
        db.query(Site).delete()
        db.commit()
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = normalize_url(row.get("url", "").strip())
            if not url:
                continue
            folder = None
            folder_name = row.get("folder", "").strip()
            if folder_name:
                folder = db.query(Folder).filter(Folder.name == folder_name).first()
                if not folder:
                    folder = Folder(name=folder_name)
                    db.add(folder)
                    db.flush()
            site = db.query(Site).filter(Site.url == url).first()
            if not site:
                site = Site(url=url)
                db.add(site)
            site.name = row.get("name", "").strip() or url
            site.folder_id = folder.id if folder else None
            site.tags_csv = row.get("tags_csv", "").strip()
            site.schedule_type = row.get("schedule_type", "interval").strip() or "interval"
            site.interval_seconds = max(int(float(row.get("interval_seconds") or 300)), 60)
            site.cron_expression = row.get("cron_expression", "").strip()
            site.threshold_percent = max(float(row.get("threshold_percent") or 0.5), 0)
            site.wait_seconds = max(int(float(row.get("wait_seconds") or 2)), 0)
            site.viewport_width = max(int(float(row.get("viewport_width") or 1440)), 320)
            site.viewport_height = max(int(float(row.get("viewport_height") or 1200)), 320)
            site.ignore_selectors = row.get("ignore_selectors", "").strip()
            site.cookie_mode = row.get("cookie_mode", "auto").strip() or "auto"
            site.enabled = _bool(row.get("enabled", "true"))
            restored += 1
    db.commit()
    return restored
