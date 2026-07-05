from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import create_session_token, current_user, ensure_admin_user, hash_password, require_admin, require_login, verify_password
from app.config import settings
from app.db import SessionLocal, get_db, init_db_with_retry
from app.models import Change, Folder, Site, User
from app.services.monitor import normalize_url, run_check
from app.services.scheduler import scheduler, start_scheduler, sync_jobs

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db_with_retry()
    db = SessionLocal()
    try:
        ensure_admin_user(db)
    finally:
        db.close()
    start_scheduler()
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)

app = FastAPI(title="Web Monitor Enterprise 6", version="6.0.0", lifespan=lifespan)
app.mount("/data", StaticFiles(directory=str(settings.data_dir)), name="data")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/health")
def health():
    return {"status": "ok", "app": "enterprise-6"}

@app.get("/api/stats")
def api_stats(db: Session = Depends(get_db)):
    return {
        "sites": db.query(Site).count(),
        "enabled": db.query(Site).filter(Site.enabled == True).count(),
        "changed": db.query(Change).filter(Change.status == "changed").count(),
        "errors": db.query(Change).filter(Change.status == "error").count(),
    }

@app.get("/api/sites")
def api_sites(db: Session = Depends(get_db)):
    return db.query(Site).order_by(Site.id).all()

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username, User.active == True).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Ungültiger Login"}, status_code=401)
    response = RedirectResponse("/", status_code=303)
    response.set_cookie("session", create_session_token(username), httponly=True, samesite="lax")
    return response

@app.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("session")
    return response

@app.get("/")
def dashboard(request: Request, q: str = "", db: Session = Depends(get_db)):
    redirect = require_login(request, db)
    if redirect:
        return redirect
    query = db.query(Site)
    if q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(or_(Site.name.ilike(like), Site.url.ilike(like), Site.tags_csv.ilike(like)))
    sites = query.order_by(Site.id.desc()).all()
    changes = db.query(Change).order_by(Change.id.desc()).limit(50).all()
    stats = {
        "sites": db.query(Site).count(),
        "enabled": db.query(Site).filter(Site.enabled == True).count(),
        "changed": db.query(Change).filter(Change.status == "changed").count(),
        "errors": db.query(Change).filter(Change.status == "error").count(),
    }
    return templates.TemplateResponse("index.html", {"request": request, "sites": sites, "changes": changes, "stats": stats, "q": q, "user": current_user(request, db)})

@app.get("/sites/{site_id}")
def site_detail(site_id: int, request: Request, db: Session = Depends(get_db)):
    redirect = require_login(request, db)
    if redirect:
        return redirect
    site = db.get(Site, site_id)
    changes = db.query(Change).filter(Change.site_id == site_id).order_by(Change.id.desc()).limit(100).all()
    return templates.TemplateResponse("site.html", {"request": request, "site": site, "changes": changes})

@app.post("/sites")
def create_site(
    request: Request,
    name: str = Form(""),
    url: str = Form(...),
    folder_name: str = Form(""),
    tags_csv: str = Form(""),
    schedule_type: str = Form("interval"),
    interval_seconds: int = Form(300),
    cron_expression: str = Form(""),
    threshold_percent: float = Form(0.5),
    wait_seconds: int = Form(2),
    viewport_width: int = Form(1440),
    viewport_height: int = Form(1200),
    ignore_selectors: str = Form(""),
    cookie_mode: str = Form("auto"),
    db: Session = Depends(get_db),
):
    redirect = require_login(request, db)
    if redirect:
        return redirect
    folder = None
    if folder_name.strip():
        folder = db.query(Folder).filter(Folder.name == folder_name.strip()).first()
        if not folder:
            folder = Folder(name=folder_name.strip())
            db.add(folder)
            db.flush()
    site = Site(
        name=name.strip() or normalize_url(url),
        url=normalize_url(url),
        folder_id=folder.id if folder else None,
        tags_csv=tags_csv.strip(),
        schedule_type=schedule_type,
        interval_seconds=max(interval_seconds, 60),
        cron_expression=cron_expression.strip(),
        threshold_percent=max(threshold_percent, 0),
        wait_seconds=max(wait_seconds, 0),
        viewport_width=max(viewport_width, 320),
        viewport_height=max(viewport_height, 320),
        ignore_selectors=ignore_selectors.strip(),
        cookie_mode=cookie_mode,
        enabled=True,
    )
    db.add(site)
    db.commit()
    sync_jobs()
    return RedirectResponse("/", status_code=303)

@app.post("/sites/{site_id}/edit")
def edit_site(
    site_id: int,
    request: Request,
    name: str = Form(""),
    url: str = Form(...),
    tags_csv: str = Form(""),
    schedule_type: str = Form("interval"),
    interval_seconds: int = Form(300),
    cron_expression: str = Form(""),
    threshold_percent: float = Form(0.5),
    wait_seconds: int = Form(2),
    viewport_width: int = Form(1440),
    viewport_height: int = Form(1200),
    ignore_selectors: str = Form(""),
    cookie_mode: str = Form("auto"),
    enabled: str | None = Form(None),
    db: Session = Depends(get_db),
):
    redirect = require_login(request, db)
    if redirect:
        return redirect
    site = db.get(Site, site_id)
    if site:
        site.name = name.strip() or normalize_url(url)
        site.url = normalize_url(url)
        site.tags_csv = tags_csv.strip()
        site.schedule_type = schedule_type
        site.interval_seconds = max(interval_seconds, 60)
        site.cron_expression = cron_expression.strip()
        site.threshold_percent = max(threshold_percent, 0)
        site.wait_seconds = max(wait_seconds, 0)
        site.viewport_width = max(viewport_width, 320)
        site.viewport_height = max(viewport_height, 320)
        site.ignore_selectors = ignore_selectors.strip()
        site.cookie_mode = cookie_mode
        site.enabled = enabled == "on"
        db.commit()
    sync_jobs()
    return RedirectResponse(f"/sites/{site_id}", status_code=303)

@app.post("/sites/{site_id}/check")
def manual_check(site_id: int, request: Request, db: Session = Depends(get_db)):
    redirect = require_login(request, db)
    if redirect:
        return redirect
    run_check(db, site_id)
    sync_jobs()
    return RedirectResponse(f"/sites/{site_id}", status_code=303)

@app.post("/sites/{site_id}/delete")
def delete_site(site_id: int, request: Request, db: Session = Depends(get_db)):
    redirect = require_login(request, db)
    if redirect:
        return redirect
    site = db.get(Site, site_id)
    if site:
        db.delete(site)
        db.commit()
    sync_jobs()
    return RedirectResponse("/", status_code=303)

@app.post("/sites/{site_id}/reset-baseline")
def reset_baseline(site_id: int, request: Request, db: Session = Depends(get_db)):
    redirect = require_login(request, db)
    if redirect:
        return redirect
    site = db.get(Site, site_id)
    if site:
        site.baseline_path = ""
        site.last_status = "baseline reset"
        site.last_error = ""
        db.commit()
    return RedirectResponse(f"/sites/{site_id}", status_code=303)

@app.get("/admin/users")
def users_page(request: Request, db: Session = Depends(get_db)):
    redirect = require_admin(request, db)
    if redirect:
        return redirect
    return templates.TemplateResponse("users.html", {"request": request, "users": db.query(User).order_by(User.id).all()})

@app.post("/admin/users")
def create_user(request: Request, username: str = Form(...), password: str = Form(...), role: str = Form("user"), db: Session = Depends(get_db)):
    redirect = require_admin(request, db)
    if redirect:
        return redirect
    db.add(User(username=username.strip(), password_hash=hash_password(password), role=role, active=True))
    db.commit()
    return RedirectResponse("/admin/users", status_code=303)
