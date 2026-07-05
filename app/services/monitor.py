from datetime import datetime
from pathlib import Path
from app.config import settings
from app.models import Site, Change
from app.services.compare import compare_images
from app.services.screenshot import capture_screenshot

def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def public_path(path: Path) -> str:
    return str(path).replace(str(settings.data_dir), "/data")

def classify_relevance(percent: float, error: str = "") -> tuple[bool, str]:
    if error:
        return True, "Fehler beim Check."
    if percent >= 5:
        return True, "Große visuelle Änderung."
    if percent >= 0.5:
        return True, "Änderung über Schwelle."
    return False, "Kleine Änderung, wahrscheinlich nicht relevant."

def run_check(db, site_id: int) -> Change:
    site = db.get(Site, site_id)
    if not site:
        raise ValueError("Site not found")

    site.url = normalize_url(site.url)
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    shot = settings.screenshot_dir / f"site-{site.id}" / f"{stamp}.png"
    diff = settings.diff_dir / f"site-{site.id}" / f"{stamp}.png"
    change = Change(site_id=site.id, checked_at=datetime.utcnow())

    try:
        http_status, duration_ms = capture_screenshot(
            site.url,
            shot,
            site.viewport_width,
            site.viewport_height,
            site.wait_seconds,
            site.ignore_selectors,
            site.cookie_mode,
        )
        change.http_status = http_status
        change.duration_ms = duration_ms
        site.last_http_status = http_status
        site.last_duration_ms = duration_ms
        change.screenshot_path = public_path(shot)

        if not site.baseline_path:
            site.baseline_path = str(shot)
            site.last_status = "baseline"
            change.status = "baseline"
            change.relevant = False
            change.relevance_reason = "Baseline erstellt."
        else:
            changed, percent = compare_images(Path(site.baseline_path), shot, diff)
            change.difference_percent = percent
            relevant, reason = classify_relevance(percent)
            change.relevant = relevant
            change.relevance_reason = reason

            if changed and percent >= site.threshold_percent:
                change.changed = True
                change.status = "changed"
                change.diff_path = public_path(diff)
                site.baseline_path = str(shot)
                site.last_status = "changed"
            else:
                change.status = "unchanged"
                site.last_status = "unchanged"

        site.last_error = ""

    except Exception as exc:
        change.status = "error"
        change.error = str(exc)
        change.relevant = True
        change.relevance_reason = "Fehler beim Check."
        site.last_status = "error"
        site.last_error = str(exc)

    site.last_checked_at = datetime.utcnow()
    db.add(change)
    db.commit()
    db.refresh(change)
    return change
