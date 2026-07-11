from pathlib import Path

base = Path("app/templates/base.html")
text = base.read_text(encoding="utf-8")

theme_tag = '<script src="/static/theme.js"></script>'
css_tag = '<link href="/static/table-darkmode-force.css" rel="stylesheet">'

if css_tag not in text:
    marker = '<link href="/static/app.css" rel="stylesheet">'
    if marker in text:
        text = text.replace(marker, marker + "\n  " + css_tag, 1)
    else:
        text = text.replace("</head>", "  " + css_tag + "\n</head>", 1)

if theme_tag not in text:
    text = text.replace("</body>", "  " + theme_tag + "\n</body>", 1)

base.write_text(text, encoding="utf-8")
print("Darkmode-Tabellenfix eingebunden.")
