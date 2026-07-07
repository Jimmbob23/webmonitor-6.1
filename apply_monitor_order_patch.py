from pathlib import Path

p = Path("app/templates/index.html")
text = p.read_text(encoding="utf-8")

start_card = text.find('<div class="card mb-4">')
start_table = text.find('<table class="table table-darkish align-middle">')
end_table = text.find('</table>', start_table)

if start_card == -1 or start_table == -1 or end_table == -1:
    raise SystemExit("Konnte Formular/Tabelle nicht eindeutig finden.")

end_table += len('</table>')

form_block = text[start_card:start_table]
table_block = text[start_table:end_table]

# Bestehende Reihenfolge: Formular -> Tabelle
# Neue Reihenfolge: Tabelle -> Formular
if start_card < start_table:
    new_text = text[:start_card]
    new_text += '<h2>Angelegte Monitore</h2>\n'
    new_text += table_block.replace('<table class="table table-darkish align-middle">', '<table class="table table-darkish align-middle mb-4">', 1)
    new_text += "\n\n"
    new_text += form_block
    new_text += text[end_table:]
else:
    new_text = text

# Falls schon eine alte Überschrift doppelt vorhanden ist, grob bereinigen
new_text = new_text.replace('<h2>Angelegte Monitore</h2>\n<h2>Angelegte Monitore</h2>', '<h2>Angelegte Monitore</h2>')

p.write_text(new_text, encoding="utf-8")
print("index.html angepasst: Monitorliste steht jetzt vor der Eingabemaske.")
