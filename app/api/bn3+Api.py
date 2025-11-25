import os
import tempfile

import whisper
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Whisper Transcription API")

# CORS Middleware für React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React Dev Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Whisper Modell laden (beim Start der Anwendung)
# Optionen: "tiny", "base", "small", "medium", "large"
# "base" ist ein guter Kompromiss zwischen Geschwindigkeit und Genauigkeit
model = whisper.load_model("tiny")


@app.get("/")
async def root():
    return {"message": "Whisper Transcription API ist aktiv"}


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Empfängt eine MP3-Datei und gibt die Transkription zurück
    """
    # Überprüfen, ob es eine MP3-Datei ist
    if not file.filename.endswith('.mp3'):
        raise HTTPException(status_code=400, detail="Nur MP3-Dateien werden unterstützt")

    try:
        # Temporäre Datei erstellen
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            # Datei speichern
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Whisper Transkription durchführen
        result = model.transcribe(tmp_file_path, language="de")  # "de" für Deutsch, None für automatisch

        # Temporäre Datei löschen
        os.unlink(tmp_file_path)

        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "filename": file.filename
        }

    except Exception as e:
        # Temporäre Datei aufräumen, falls vorhanden
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

        raise HTTPException(status_code=500, detail=f"Fehler bei der Transkription: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "whisper-base"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)