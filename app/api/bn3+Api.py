import os
import subprocess
import tempfile
import pathlib
import json

import whisper
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.services.mp3TranscriptionService import Mp3TranscriptionService

app = FastAPI(title="Whisper Transcription API")

# CORS Middleware für React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React Dev Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mp3_transcription_service = Mp3TranscriptionService()

TARGET_SR = 16000

async def read_and_parse_pm3(mp3_file):
    print("test")
    try:
        # Tempdatei speichern
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(mp3_file)
            tmp_file_path = pathlib.Path(tmp_file.name).as_posix()
        tmp_file.close()
        tmp_file_wav = tmp_file_path.split(".")[0]+".wav"
        print(f"Konvertiere {tmp_file_path} → {tmp_file_wav} ...")
        cmd = f'ffmpeg -y -i "{tmp_file_path}" -ar {TARGET_SR} -ac 1 "{tmp_file_wav}"'
        subprocess.run(cmd, shell=True, check=True)
        os.remove(tmp_file_path)
        return tmp_file_wav
    except Exception as e:
        raise HTTPException(500, f"Fehler beim Parsen des Mp3 Files: {str(e)}")


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
        audio_file_wav = await read_and_parse_pm3(content)
        text_segments = mp3_transcription_service.transcribe_audio(audio_file_wav)
        speaker_segments = mp3_transcription_service.run_diarization(audio_file_wav)
        merged = mp3_transcription_service.assign_speaker_to_segment(text_segments, speaker_segments)
        final_json = mp3_transcription_service.build_final_json(audio_file_wav,merged)
        os.remove(audio_file_wav)
        return final_json

    except Exception as e:

        raise HTTPException(500, f"Fehler bei der Transkription: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)