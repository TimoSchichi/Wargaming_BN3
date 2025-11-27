import os
import json
from datetime import datetime

import whisper
from pyannote.audio import Pipeline
from huggingface_hub import login


# ==========================
# 0. KONFIGURATION
# ==========================

# Pfad zur Audiodatei
AUDIO_FILE =  "/home/user2/Desktop/Test/Daten/wargaming/hkt_wargaming_audio_16k.wav"


# Pfad zur Ausgabe-JSON
OUTPUT_JSON = "diarization.json"

# Whisper-Modell auswählen: "tiny", "base", "small", "medium", "large"
WHISPER_MODEL_NAME = "medium"

# HuggingFace-Token aus Umgebungsvariable lesen: vorher in der Shell z. B.:
# export HF_TOKEN="dein_token_hier"
HF_TOKEN = os.getenv("")


# ==========================
# 1. ASR MIT WHISPER
# ==========================

def transcribe_audio(audio_path: str):
    """
    Transkribiert Audio mit Whisper und gibt eine Liste von Segmenten zurück:
    [
      {"start": float, "end": float, "text": str},
      ...
    ]
    """
    print(f"Lade Whisper-Modell '{WHISPER_MODEL_NAME}'...")
    model = whisper.load_model(WHISPER_MODEL_NAME)

    print("Starte Transkription...")
    result = model.transcribe(audio_path, verbose=False)

    segments = []
    for seg in result["segments"]:
        segments.append({
            "start": float(seg["start"]),
            "end": float(seg["end"]),
            "text": seg["text"].strip()
        })

    print(f"Transkription fertig. Segmente: {len(segments)}")
    return segments


# ==========================
# 2. SPRECHER-DIARISIERUNG MIT PYANNOTE
# ==========================




# ==========================
# 3. MERGEN: TEXT + SPRECHER
# ==========================

def assign_speaker_to_segment(text_segments, speaker_segments):
    """
    Nimmt Whisper-Segmente und ordnet jedem Segment den passenden Sprecher zu.
    Ansatz: wir nehmen die Mitte des Textsegments und schauen,
    welcher Sprecher zu dieser Zeit aktiv ist.
    """
    merged = []

    for seg in text_segments:
        seg_mid = (seg["start"] + seg["end"]) / 2.0
        speaker_label = None

def run_diarization(audio_path: str):
    """
    Führt Speaker-Diarization mit PyAnnote durch und gibt eine Liste von
    Sprecher-Zeitsegmenten zurück:
    [
      {"start": float, "end": float, "speaker": "SPEAKER_00"},
      ...
    ]
    Funktioniert mit pyannote.audio 3.x (Annotation) und 4.x (DiarizeOutput).
    """
    print("Login bei HuggingFace...")
    login(token=HF_TOKEN)

    print("Lade PyAnnote-Pipeline...")
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=HF_TOKEN
    )

    # Optional: GPU nutzen, falls verfügbar
    import torch
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print("Nutze CUDA für Diarisierung.")
    else:
        device = torch.device("cpu")
        print("Nutze CPU für Diarisierung.")

    pipeline.to(device)


    print("Starte Diarisierung...")
    diarization = pipeline(audio_path)

    # pyannote.audio 4.x: pipeline(...) -> DiarizeOutput mit .speaker_diarization
    # pyannote.audio 3.x: pipeline(...) -> direkt ein Annotation-Objekt
    if hasattr(diarization, "speaker_diarization"):
        annotation = diarization.speaker_diarization
    else:
        annotation = diarization  # Legacy-Verhalten

    speaker_segments = []
    for turn, _, speaker in annotation.itertracks(yield_label=True):
        speaker_segments.append({
            "start": float(turn.start),
            "end": float(turn.end),
            "speaker": str(speaker)
        })

    print(f"Diarisierung fertig. Sprecher-Segmente: {len(speaker_segments)}")
    return speaker_segments


# ==========================
# 3. MERGEN: TEXT + SPRECHER
# ==========================

def assign_speaker_to_segment(text_segments, speaker_segments):
    """
    Nimmt Whisper-Segmente und ordnet jedem Segment den passenden Sprecher zu.
    Ansatz: wir nehmen die Mitte des Textsegments und schauen,
    welcher Sprecher zu dieser Zeit aktiv ist.
    """
    merged = []

    for seg in text_segments:
        seg_mid = (seg["start"] + seg["end"]) / 2.0

        # passenden Sprecher suchen
        for sp in speaker_segments:
            if sp["start"] <= seg_mid <= sp["end"]:
                speaker_label = sp["speaker"]
                break

        # falls nichts passt, überlappenden Sprecher suchen
        if speaker_label is None:
            for sp in speaker_segments:
                overlap_start = max(seg["start"], sp["start"])
                overlap_end = min(seg["end"], sp["end"])
                if overlap_end > overlap_start:
                    speaker_label = sp["speaker"]
                    break

        # Fallback: "UNKNOWN"
        if speaker_label is None:
            speaker_label = "UNKNOWN"

        merged.append({
            "start": seg["start"],
            "end": seg["end"],
            "speaker": speaker_label,
            "text": seg["text"]
        })

    return merged


# ==========================
# 4. FINALES JSON BAUEN
# ==========================

def build_final_json(audio_file, merged_segments):
    """
    Baut ein finales JSON mit Meta-Infos und allen Segmenten:
    {
      "audio_file": "...",
      "created_at": "...",
      "speakers": [...],
      "segments": [
        {
          "start": ...,
          "end": ...,
          "speaker": "SPEAKER_00",
          "text": "..."
        },
        ...
      ]
    }
    """
    speakers = sorted(list({seg["speaker"] for seg in merged_segments}))

    data = {
        "audio_file": os.path.basename(audio_file),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "speakers": speakers,
        "segments": merged_segments
    }

    return data


# ==========================
# 5. MAIN
# ==========================

def main():
    # 1. Transkription
    text_segments = transcribe_audio(AUDIO_FILE)

    # 2. Diarisierung
    speaker_segments = run_diarization(AUDIO_FILE)

    # 3. Mergen
    merged = assign_speaker_to_segment(text_segments, speaker_segments)

    # 4. JSON bauen
    final_json = build_final_json(AUDIO_FILE, merged)

    # 5. Speichern
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)

    print(f"Fertiges JSON gespeichert unter: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
