from pathlib import Path

p = Path("app/main.py")
text = p.read_text(encoding="utf-8")

if "def _delete_public_data_file" not in text:
    marker = '@app.get("/admin/users")'
    block = '''\
def _delete_public_data_file(public_path: str):
    if not public_path or not public_path.startswith("/data/"):
        return
    try:
        file_path = (settings.data_dir / public_path.replace("/data/", "", 1)).resolve()
        data_dir = settings.data_dir.resolve()
        if data_dir in file_path.parents and file_path.is_file():
            file_path.unlink(missing_ok=True)
    except Exception:
        pass


@app.post("/changes/{change_id}/delete")
def delete_change(change_id: int, request: Request, db: Session = Depends(get_db)):
    redirect = require_login(request, db)
    if redirect:
        return redirect
    change = db.get(Change, change_id)
    site_id = None
    if change:
        site_id = change.site_id
        _delete_public_data_file(change.screenshot_path)
        _delete_public_data_file(change.diff_path)
        db.delete(change)
        db.commit()
    return RedirectResponse(f"/sites/{site_id}" if site_id else "/", status_code=303)


@app.post("/sites/{site_id}/history/delete")
def delete_site_history(site_id: int, request: Request, db: Session = Depends(get_db)):
    redirect = require_login(request, db)
    if redirect:
        return redirect
    site = db.get(Site, site_id)
    if site:
        for change in list(site.changes):
            _delete_public_data_file(change.screenshot_path)
            _delete_public_data_file(change.diff_path)
            db.delete(change)
        site.baseline_path = ""
        site.last_status = "history cleared"
        site.last_error = ""
        db.commit()
        sync_jobs()
    return RedirectResponse(f"/sites/{site_id}", status_code=303)


'''
    if marker not in text:
        raise SystemExit("Einfügeposition @app.get('/admin/users') nicht gefunden.")
    text = text.replace(marker, block + marker)

p.write_text(text, encoding="utf-8")
print("Cleanup-Routen eingefügt.")
