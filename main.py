from itertools import islice
from moviepy.editor import AudioFileClip, ImageClip, VideoFileClip, CompositeVideoClip, concatenate_audioclips
import os
from playwright.sync_api import sync_playwright
import praw
import random
import tomli
from pwright import Playwright

from tts import TTS

with open("conf.toml", "rb") as f:
    config = tomli.load(f)
env = config["env"]
settings = config["settings"]
width, height = 608, 1080

REDDIT_URL="https://www.reddit.com"
AUDIO_PATH=settings["AUDIO_PATH"]
IMAGE_PATH=settings["IMAGE_PATH"]

# Capture top Reddit submission's title and text, and the top N comments
reddit = praw.Reddit(
    client_id=env["REDDIT_CLIENT_ID"],
    client_secret=env["REDDIT_CLIENT_SECRET"],
    user_agent=env["REDDIT_USER_AGENT"],
)
tts = TTS(audio_path=AUDIO_PATH)
tts.disabled = False

subreddit_name = settings["SUBREDDIT"]
submissions = reddit.subreddit(subreddit_name).top(time_filter="day")
top_submission = next(s for s in submissions if not s.stickied)

print(top_submission.title + ". " + top_submission.selftext)
tts.save_tts(top_submission.title + ". " + top_submission.selftext)

# Capture screenshots of the Reddit data gathered
with sync_playwright() as p_ctx:
    p = Playwright(p_ctx, image_path=IMAGE_PATH)

    p.page.goto(REDDIT_URL + top_submission.permalink + "?sort=top")
    p.page.wait_for_load_state("networkidle")

    p.screenshot(
        f"#t3_{top_submission.id}",
    )

    top_submission.comment_sort = "top"
    for comment in islice((x for x in top_submission.comments if not x.stickied), settings.get("NUM_COMMENTS", 3)):
        print(comment.body)
        tts.save_tts(comment.body)
        p.screenshot_between((
            f'[thingid=t1_{comment.id}]',
            f"#t1_{comment.id}-next-reply"
        ))

        # Screenshot & TTS for reply
        reply = comment.replies[0] if comment.replies else None
        print(reply.body)
        tts.save_tts(reply.body)
        p.screenshot_between((
            f'[thingid=t1_{comment.id}]',
            f'#t1_{reply.id}-next-reply'
        ), alt_selector=f"faceplate-partial[slot=children-t1_{comment.id}-0]")
    
    p.browser.close()

audio_filepaths = sorted(os.path.join(AUDIO_PATH, f) for f in os.listdir(AUDIO_PATH) if f.endswith('.mp3'))
image_filepaths = sorted(os.path.join(IMAGE_PATH, f) for f in os.listdir(IMAGE_PATH) if f.endswith('.png'))
audio_filepaths.append("assets/outro.mp3")
image_filepaths.append("assets/outro.png")

audio_clips = [AudioFileClip(audio_file) for audio_file in audio_filepaths]
total_duration = sum(audio.duration for audio in audio_clips)

background = VideoFileClip("assets/backgrounds/parkour_background.mp4")
start = random.uniform(0, background.duration - total_duration)
background = background.subclip(start, start + total_duration)

image_clips = []
clip_start = 0
for audio, image_file in zip(audio_clips, image_filepaths):
    image_clip = ImageClip(image_file, duration=audio.duration).resize(width=width)
    y_pos = 0.1 if (image_clip.h > height / 2) else 0.2
    image_clip = image_clip.set_start(clip_start)
    image_clip = image_clip.set_position(("center", y_pos), relative=True)

    image_clips.append(image_clip)
    clip_start += audio.duration


chained_audio = concatenate_audioclips(audio_clips)
video_clip = CompositeVideoClip([background, *image_clips], use_bgclip=True)
final_video = video_clip.set_audio(chained_audio)
final_video.write_videofile(
    "output.mp4",
    fps=24,
    codec='libx264', 
    audio_codec='aac', 
    temp_audiofile='temp-audio.m4a', 
    remove_temp=True
)

