# python code to load data from the Azure Blob Storage

# Imports
import os
import paramiko
import stat
from pathlib import Path

# Load environment variables from .env file
HOST = os.getenv("SFTP_HOST")
PORT = int(os.getenv("SFTP_PORT"))
USERNAME = os.getenv("SFTP_USERNAME")
PASSWORD = os.getenv("SFTP_PASSWORD")


# Class to download files from Azure Blob Storage
class AzureSFTPDownloader:
    """
    Ein einfacher SFTP-Downloader für Azure.
    """

    def __init__(self, host: str, port: int, username: str, password: str, remote_dir: str = "."):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.remote_dir = remote_dir
        self.ssh = None
        self.sftp = None

    # --- Verbindung ---
    def connect(self):
        """
        Stellt die Verbindung zum SFTP-Server her.
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            look_for_keys=False,
        )
        self.sftp = self.ssh.open_sftp()
        print("Connection successfully established ... ")

    def close(self):
        """
        Schließt die SFTP- und SSH-Verbindungen.
        """
        try:
            if self.sftp:
                self.sftp.close()
        finally:
            self.sftp = None
            if self.ssh:
                self.ssh.close()
                self.ssh = None
            print("Connection closed.")

    # --- Listing ---
    def listdir(self, path: str = None) -> list:
        """
        Listet die Dateien im angegebenen Verzeichnis auf.

        Args:
            path (str): Das Verzeichnis, dessen Dateien aufgelistet werden sollen.

        Returns:
            list: Eine Liste der Dateien im angegebenen Verzeichnis.
        """
        self._ensure_connected()
        path = path or self.remote_dir
        print(f"lists of files {self.sftp.listdir(path)}")
        return self.sftp.listdir_attr(path)

    # --- Download: alle Dateien -> data/bronze im Projektroot ---
    def download_all_to_bronze(self, remote_dir: str = None) -> None:
        """
        Lädt alle REGULÄREN Dateien aus remote_dir (nicht rekursiv) nach <project-root>/data/bronze.
        Wenn das aktuelle CWD 'notebooks' heißt, wird eine Ebene höher gespeichert.

        Args:
            remote_dir (str): Das Remote-Verzeichnis, aus dem die Dateien heruntergeladen werden sollen.
        """
        self._ensure_connected()
        rdir = remote_dir or self.remote_dir

        # Zielordner: Projektroot/data/bronze
        base = Path("/workspace/data/bronze")
        print(f"Lokaler Zielordner: {base.resolve()}")

        for entry in self.sftp.listdir_attr(rdir):
            # Nur reguläre Dateien (keine Ordner/Symlinks)
            if not stat.S_ISREG(entry.st_mode):
                continue
            remote_path = f"{rdir.rstrip('/')}/{entry.filename}"
            local_path = base / entry.filename
            print(f"Lade herunter: {remote_path} -> {local_path}")
            self._download_file(remote_path, local_path)

    # --- Helpers ---
    def _download_file(self, remote_path: str, local_path: Path) -> None:
        """
        Lädt eine Datei vom SFTP-Server herunter.

        Args:
            remote_path (str): Der Pfad zur Remote-Datei.
            local_path (Path): Der Pfad zur lokalen Zieldatei.
        """
        self._ensure_connected()
        local_path.parent.mkdir(parents=True, exist_ok=True)
        # Prefetch AUS für Azure SFTP → vermeidet "unimplemented"
        self.sftp.get(remote_path, str(local_path), prefetch=False)
        print(f"Gespeichert: {local_path} ({local_path.stat().st_size} Bytes)")

    def _ensure_connected(self):
        if not self.sftp:
            raise RuntimeError("SFTP-Verbindung nicht aktiv.")

# Hauptprogramm
if __name__ == "__main__":
    # init class
    client = AzureSFTPDownloader(HOST, PORT, USERNAME, PASSWORD, remote_dir=".")

    client.connect()
    client.listdir(".")                 
    client.download_all_to_bronze(".")  
    client.close()
