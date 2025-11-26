import base64
import json
import requests


class Mp3TranscriptionService:

    API_KEY = "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"  # z.B. "sk-or-..."
    MODEL = "openai/gpt-4o-audio-preview" # Audio-fähiges Modell auf OpenRouter

    def transcript_audio_with_speakers(self, audio_file_path):
        #Get Audio as Base64
        with open(audio_file_path, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")

        #Create Request Payload
        payload = {
            "model": self.MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Transkribiere dieses Audio vollständig auf Deutsch. "
                                "Erkenne automatisch die verschiedenen Sprecher und "
                                "nummeriere sie als 'Sprecher 1:', 'Sprecher 2:' usw. "
                                "Jeder Sprecherwechsel soll in einer neuen Zeile "
                                "stehen. "
                                "Gib NUR das Transkript aus (keine Erklärungen)."
                            ),
                        },
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_base64,
                                "format": "mp3",
                            },
                        },
                    ],
                }
            ],
            "stream": False,
        }

        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json",
        }
        print("test")
        #Send Request to OpenRouter
        try:
            resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            )
            print(resp.content)
            resp.raise_for_status()
            print("test2")
            data = resp.json()
            print("test3")
            # Get Text from Response
            text = data["choices"][0]["message"]["content"]

            return text
        except Exception as e:
            print(str(e))
            return "kaputt"