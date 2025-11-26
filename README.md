# Setup und Installation

# Ubuntu

# 1. Frontend

### 1. NVM installieren
```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```
### 2. NodeJS 25.2.1 installieren
```
 nvm install 25.2.1
 ```
### 3. Installation prüfen
```
node -v
npm -v 
```

### 2. Installation von tailwindcss
```
npm install -D tailwindcss postcss autoprefixer
```
Wichtig: Dieser Befehl muss vor dem ersten Start der React Anwendung und vor der Installation der Node Module ausgeführt werden!

### 3. Installation der Node Modules
Beim Change Directory bitte den den Pfad zum Bn3 Ordner des Projekts nehmen!
```
cd ../frontend/bn3
npm install
```

### 4. Start der React Anwendung
Beim Change Directory bitte den den Pfad zum Bn3 Ordner des Projekts nehmen!
```
cd path/to/root/bn3
npm start
```

Die Frontend-Anwendung wird im Browser geöffnet
# 2. Backend

### 1. Installation von Python
```
sudo apt install python3.10
```

### 2.
* Python Interpreter in der IDE konfigurieren
* Virtual Environment erstellen

### 3. Installation der benötigten Python Packages im Virtual Environment
```
cd path/to/api/directory/api
pip install -r requirements.txt
```

### 4. Backend Starten
* bn3+Api.py ausführen
* Die Api läuft local im Terminal und ist über localhost:8000 im Browser erreichbar
* Die Dokumentation mit Integriertem Test der Endpunkte ist unter localhost:8000/docs zu finden





