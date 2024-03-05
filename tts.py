from google.cloud import texttospeech

class TTS():

    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            effects_profile_id=["handset-class-device"],
            speaking_rate=1.25,
        )
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-au",
            name="en-AU-Polyglot-1",
        )
        self.disabled = False

    def save_tts(self, text, filepath: str):
        if self.disabled or not text or len(text) > 400:
            return

        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=self.voice, audio_config=self.audio_config
        )
        with open(filepath, "wb") as out:
            out.write(response.audio_content)