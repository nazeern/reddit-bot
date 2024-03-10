from google.cloud import texttospeech

class TTS():

    def __init__(self, audio_path):
        self.audio_path = audio_path
        self.client = texttospeech.TextToSpeechClient()
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            effects_profile_id=["handset-class-device"],
            speaking_rate=1.30,
        )
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-J",
        )
        self.disabled = False
        self.i = 0

    def save_tts(self, text: str, filepath: str = None):
        if self.disabled or not text:
            return

        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=self.voice, audio_config=self.audio_config
        )
        with open(filepath or f"{self.audio_path}/clip{self.i}.mp3", "wb") as out:
            out.write(response.audio_content)
        self.i += 1