from pathlib import Path

p = Path("app/main.py")
text = p.read_text(encoding="utf-8")

if "def _delete_public_data_file" in text and '@app.post("/changes/{change_id}/delete")' in text:
    print("Lösch-Routen sind bereits vorhanden.")
    raise SystemExit(0)

block = """
def _delete_public_data_file(public_path: str):
    if not public_path:
        return
    if not public_path.startswith("/data/"):
        return

    try:
        relative = public_path.replace("/data/", "", 1)
        file_path = (settings.data_dir / relative).resolve()
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

    if site_id:
        return RedirectResponse(f"/sites/{site_id}", status_code=303)

    return RedirectResponse("/", status_code=303)


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


"""

markers = [
    '@app.get("/admin/users")',
    '@app.get("/backups")',
    '@app.get("/api/stats")',
]

inserted = False
for marker in markers:
    if marker in text:
        text = text.replace(marker, block + marker, 1)
        inserted = True
        break

if not inserted:
    text = text.rstrip() + "\n\n" + block

p.write_text(text, encoding="utf-8")
print("Lösch-Routen wurden in app/main.py eingefügt.")
