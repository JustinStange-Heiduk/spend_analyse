Spend-Analyse (Baseline Setup)
Minimaler Projekt-Start für eine Python‑basierte Spend‑Analyse mit:

VS Code Devcontainer (empfohlenes Dev‑Setup)

Docker (schlankes Python 3.11‑Image)

Basics für spätere SFTP‑Anbindung und Pandas‑Analysen

Fokus aktuell: saubere, reproduzierbare Umgebung. Die eigentliche Analyse‑Logik kommt anschließend.

-------------------------------------------------------------------------------

Projektstruktur (Stand August 2025)
.
├── .devcontainer/
│   └── devcontainer.json                                # VS Code Devcontainer-Konfiguration
├── data/
│   ├── bronze/                                          # Rohdaten (z. B. Rechnungen direkt vom SFTP)
│   │   └── Rechnungen_SAP_2023.csv
|   |   └── ...
│   ├── silver/                                          # Transformierte Daten (z. B. mit Wechselkurs angereichert)
│   │   └── Rechnungen_SAP_2023_2024.csv
|   |   └── ...
│   ├── gold/                                            # Finalisierte Auswertungen (Tabellenexport)
│   │   └── auswertung_1_2023.csv
|   |   └── ...
│   └── wechselkurse.csv                                 # Automatisch generierter Wechselkurs-Datensatz
│
├── env/
│   ├── .env                                             # Lokale Secrets (nicht tracken)
│   └── .env.example                                     # Beispielkonfiguration für SFTP & API-Zugriff
│
├── notebooks/                                           # notebooks für daten exloration und funktion testing
│   ├── bronze_notebook_load_data.ipynb   
│   ├── silver_notebook_data_transformation.ipynb
│   └── gold_notebook_auswertungen.ipynb
│
├── src/                                                 # python script zum ausführen von extract, transformation und die auswertungen
│   ├── bronze_script_load_data.py
│   ├── silver_script_data_transformation.py
│   └── gold_auswertungen.py
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt                   # pandas, numpy, paramiko, dotenv
└── README.md


-------------------------------------------------------------------------------

Was wird ausgewertet?

Die Auswertung erfolgt auf Basis von Rechnungsdaten aus SAP. Ziel ist es, zentrale Kennzahlen zur Ausgabenstruktur der Beispielfirma zu ermitteln. Dabei wird die Datenqualität durch ein mehrstufiges Transformationsmodell (Bronze → Silver → Gold) sichergestellt.

Die folgenden drei Auswertungen werden durchgeführt:

Top 10 Lieferanten nach Spend in EUR
 Aggregation der Ausgaben pro Lieferant (Rechnungswährung → EUR umgerechnet).

Top 10 Sachkonten nach Anzahl der Rechnungen
 Zählung der Belege pro Sachkonto (inkl. Mapping auf Namen).

Monatlicher Spend-Verlauf 2023–2024
 Zeitliche Verteilung der Ausgaben auf Basis des Belegdatums, gruppiert nach Jahr und Monat.

-------------------------------------------------------------------------------

Wechselkursdaten (Frankfurt API)

Für die Umrechnung von z. B. USD oder GBP in EUR wird automatisch ein Wechselkurs-DataFrame erzeugt, basierend auf der API der Europäischen Zentralbank (Standort Frankfurt).
Falls keine lokale Datei vorhanden ist, wird die Zeitreihe bei Bedarf abgerufen (Zeitraum: 01.01.2023 – 31.12.2024) und unter data/silver/wechselkurse.csv gespeichert.

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

Beim Öffnen des Projekts in Visual Studio Code mit dem Devcontainer-Setup werden die folgenden Skripte automatisch ausgeführt:

python3 /workspace/src/bronze_script_load_data.py
python3 /workspace/src/silver_script_data_transformation.py
python3 /workspace/src/gold_auswertungen.py


Diese befinden sich in der Datei .devcontainer/devcontainer.json unter dem Schlüssel:

"postStartCommand": "python3 /workspace/src/bronze_script_load_data.py && python3 /workspace/src/silver_script_data_transformation.py && python3 /workspace/src/gold_auswertungen.py && echo 'Devcontainer ist fertig gebaut und einsatzbereit. '"


Hinweis:
Falls du nicht möchtest, dass die Analyse bei jedem Start automatisch ausgeführt wird (z. B. für manuelles Debugging oder schrittweises Testen), kannst du diese Zeile einfach auskommentieren oder löschen:

// "postStartCommand": "python3 ...",

-------------------------------------------------------------------------------

# Git Verlauf checken
git log --oneline --decorate --graph

# Git Datenänderungen als txt Datei 
git log --stat > GIT_LOG.txt

