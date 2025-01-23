# Verwenden Sie ein offizielles Python-Laufzeit-Image als Basis
FROM python:3.9-slim

# Setzen Sie das Arbeitsverzeichnis
WORKDIR /app

# Kopieren Sie die requirements.txt und installieren Sie die Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Erstellen Sie das Verzeichnis für die Schriftarten und kopieren Sie die Schriftartdatei
RUN mkdir -p fonts
COPY fonts/RobotoSlab-Regular.ttf fonts/

# Kopieren Sie den Rest des Anwendungscodes
COPY main.py .

# Exponieren Sie den Port, auf dem die App läuft
EXPOSE 8080

# Definieren Sie die Umgebungsvariable für den API-Schlüssel
ENV API_KEY=IhrGeheimerAPIKey

# Starten Sie die Anwendung
CMD ["python", "main.py"]
