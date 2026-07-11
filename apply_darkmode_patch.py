from pathlib import Path

base = Path("app/templates/base.html")
text = base.read_text(encoding="utf-8")

script_tag = '<script src="/static/theme.js"></script>'

if script_tag not in text:
    if "<head>" in text:
        text = text.replace("<head>", "<head>\n  " + script_tag, 1)
    else:
        raise SystemExit("Kein <head>-Element in app/templates/base.html gefunden.")

base.write_text(text, encoding="utf-8")
print("theme.js wurde in base.html eingebunden.")
