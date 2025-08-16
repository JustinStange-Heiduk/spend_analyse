Spend-Analyse (Baseline Setup)
Minimaler Projekt-Start für eine Python‑basierte Spend‑Analyse mit:

VS Code Devcontainer (empfohlenes Dev‑Setup)

Docker (schlankes Python 3.11‑Image)

Basics für spätere SFTP‑Anbindung und Pandas‑Analysen

Fokus aktuell: saubere, reproduzierbare Umgebung. Die eigentliche Analyse‑Logik kommt anschließend.

Ordnerstruktur (Stand jetzt)
bash
Kopieren
Bearbeiten
.
├── .devcontainer/
│   └── devcontainer.json        # VS Code Devcontainer-Konfiguration
├── Dockerfile                   # Schlankes Python 3.11-Image
├── docker-compose.yml           # Service "spendapp" + Volume-Mount
├── requirements.txt             # Minimale Dependencies (pandas, paramiko
dotenv, numpy)
└── README.md                    # (dieses Dokument)

Geplant (später):
├── src/                         # Python-Source (SFTP-Loader, Transform, CLI)
├── notebooks/                   # Interaktiver Code zum Testen
├── data/                        # Ergebnis-CSV (git-ignored)
└── .env                         # lokale Secrets (NICHT committen)

-------------------------------------------------------------------------------

.env-Konfiguration

Vor dem Start des Containers müssen die Zugangsdaten zum SFTP-Server konfiguriert werden.

Vorlage kopieren

cp env/.env.example env/.env


Echte Werte eintragen (Host, Benutzername, Passwort oder SSH-Key-Pfad).

Beispiel (env/.env.example):

# SFTP Server-Verbindung
SFTP_HOST=your-sftp-host
SFTP_PORT=22
SFTP_USERNAME=your-username
SFTP_PASSWORD=your-password
SFTP_PKEY_PATH=
SFTP_REMOTE_DIR=/
CSV_PATTERN=*.csv
FX_RATES_REMOTE_PATH=


Fallback-Mechanismus
In docker-compose.yml sind zwei env_file-Einträge definiert:

env_file:
  - env/.env           # Echte Werte, falls vorhanden
  - env/.env.example   # Platzhalter als Fallback


Falls keine .env existiert, verwendet der Container automatisch die Platzhalterwerte aus .env.example.
→ Container baut immer, egal ob Zugangsdaten vorhanden sind.
-------------------------------------------------------------------------------

Voraussetzungen
    Docker Desktop (WSL2 unter Windows)
    Visual Studio Code + Extension Dev Containers

Empfohlener Weg: „Open in Container“ (VS Code)
Repo-Ordner in VS Code öffnen.

Command Palette (F1) → Dev Containers: Reopen in Container.

VS Code baut das Image (Dockerfile), startet den Service aus docker-compose.yml und mountet dein Projekt nach /workspace.

Nach dem Start siehst du im Terminal:


Devcontainer ist fertig gebaut und einsatzbereit.


Hinweis: Dieser Weg ist bevorzugt. Du musst kein docker compose up manuell ausführen – VS Code erledigt Build & Start für dich.

Alternative (optional): Docker Compose manuell
Nur wenn du ohne VS Code starten willst:

Bearbeiten
# Image bauen
docker compose build

# Container starten (im Hintergrund)
docker compose up -d

# Stoppen & aufräumen
docker compose down
In der Dev‑Routine nicht nötig; „Reopen in Container“ ist der Standard.

-------------------------------------------------------------------------------

# Git Verlauf checken
git log --oneline --decorate --graph