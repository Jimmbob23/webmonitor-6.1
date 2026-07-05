from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.db import SessionLocal
from app.models import Site
from app.services.monitor import run_check

scheduler = BackgroundScheduler(timezone="UTC")

def check_job(site_id: int):
    db = SessionLocal()
    try:
        site = db.get(Site, site_id)
        if site and site.enabled:
            run_check(db, site_id)
    finally:
        db.close()

def make_trigger(site: Site):
    if site.schedule_type == "cron" and site.cron_expression.strip():
        parts = site.cron_expression.split()
        if len(parts) == 5:
            minute, hour, day, month, day_of_week = parts
            return CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=day_of_week, timezone="UTC")
    return IntervalTrigger(seconds=max(site.interval_seconds, 60), timezone="UTC")

def sync_jobs():
    db = SessionLocal()
    try:
        existing = {job.id for job in scheduler.get_jobs()}
        wanted = set()
        for site in db.query(Site).filter(Site.enabled == True).all():
            job_id = f"site-{site.id}"
            wanted.add(job_id)
            trigger = make_trigger(site)
            current = scheduler.get_job(job_id)
            if current:
                current.reschedule(trigger)
            else:
                scheduler.add_job(check_job, trigger, args=[site.id], id=job_id, replace_existing=True, max_instances=1, coalesce=True)
        for job_id in existing - wanted:
            if job_id.startswith("site-"):
                scheduler.remove_job(job_id)
    finally:
        db.close()

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
    sync_jobs()
