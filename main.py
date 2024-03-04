from google.cloud import texttospeech
from itertools import islice
import praw

TTS_ENABLED=False

# Capture top Reddit submission's title and text, and the top N comments
reddit = praw.Reddit(
    client_id="cRGrLMWPbuzyxJ45uu8tnw",
    client_secret="iCnan1uRpuo5OGA8RD20E6PSc56Y1g",
    user_agent="shorts-bot",
)

subreddit_name = "todayilearned"
submissions = reddit.subreddit(subreddit_name).top(time_filter="day")
top_submission = next(s for s in submissions if not s.stickied)
print(top_submission.title)
print(top_submission.selftext)

top_submission.comment_sort = "top"
for comment in islice((x for x in top_submission.comments if not x.stickied), 3):
    print(comment.body)

    replies = comment.replies[:1]
    for i, reply in enumerate(replies):
        print(f"Reply {i}:\n", reply.body)

# Capture screenshots of the Reddit data gathered


# Turn this Reddit information into audio clips using Google Cloud TTS
if TTS_ENABLED:

    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=top_submission.title)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-au",
        name="en-AU-Polyglot-1",
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        effects_profile_id=["handset-class-device"]
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open("tts_audio/clip0.mp3", "wb") as out:
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')

