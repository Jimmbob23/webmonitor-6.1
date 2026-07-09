from pathlib import Path
p = Path("app/static/app.css")
text = p.read_text(encoding="utf-8") if p.exists() else ""
if "@import url('/static/responsive-cleanup.css');" not in text:
    text += "\n@import url('/static/responsive-cleanup.css');\n"
p.write_text(text, encoding="utf-8")
print("responsive-cleanup.css wurde in app.css eingebunden.")
