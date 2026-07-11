from pathlib import Path
p = Path("app/static/app.css")
text = p.read_text(encoding="utf-8") if p.exists() else ""
line = "@import url('/static/advanced-cron.css');"
if line not in text:
    text += "\n" + line + "\n"
p.write_text(text, encoding="utf-8")
print("advanced-cron.css eingebunden.")
