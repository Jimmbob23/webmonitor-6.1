# Web Monitor Enterprise 6

Sauberer Neustart ohne V4/V5-Dateimischung.

## Enthalten

- PostgreSQL
- Redis vorbereitet
- FastAPI
- Argon2 statt bcrypt/passlib
- Benutzerverwaltung mit Rollen
- editierbare Monitore
- Intervall nachträglich änderbar
- Cron-Ausdrücke
- Cookiebanner-Handling
- Playwright-Screenshots
- Diff-Bilder
- Benachrichtigungen: Webhook/Discord/Telegram/E-Mail-Grundlage
- Backups
- GitHub Actions + GHCR
- Portainer Stack
- REST API unter `/docs`

## Lokal starten

```bash
docker compose up --build
```

Aufruf:

```text
http://localhost:8005
```

Login:

```text
admin
admin123
```

## Portainer

In `stack.portainer.yml` ändern:

```yaml
image: ghcr.io/DEIN-GITHUB-BENUTZERNAME/web-monitor-enterprise-6:latest
```

Dann über GitHub Actions bauen lassen, Package öffentlich machen und deployen.
