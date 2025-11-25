import os
import tempfile
import pathlib

import whisper
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Whisper Transcription API")

# CORS Middleware für React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React Dev Server
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
    if not file.filename.endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Nur MP3-Dateien werden unterstützt")

    try:
        # Datei einlesen
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(400, "Die empfangene Datei ist leer")

        # Tempdatei speichern
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(content)
            tmp_file_path = pathlib.Path(tmp_file.name).as_posix()
        tmp_file.close()

        print("Benutze Datei:", tmp_file_path)

        # Whisper
        result = model.transcribe(tmp_file_path, language="de")

        print("tot")
        # Aufräumen
        os.unlink(tmp_file_path)

        return {
            "text": result["text"],
            "language": result.get("language", "unknown"),
            "filename": file.filename
        }

    except Exception as e:
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        raise HTTPException(500, f"Fehler bei der Transkription: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "whisper-base"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)