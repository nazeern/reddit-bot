from google.cloud import texttospeech
from itertools import islice
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import praw
import tomli

from tts import TTS

with open("conf.toml", "rb") as f:
    config = tomli.load(f)
env = config["env"]

REDDIT_URL="https://www.reddit.com"

# Capture top Reddit submission's title and text, and the top N comments
reddit = praw.Reddit(
    client_id=env["REDDIT_CLIENT_ID"],
    client_secret=env["REDDIT_CLIENT_SECRET"],
    user_agent=env["REDDIT_USER_AGENT"],
)
tts = TTS()
tts.disabled = True

subreddit_name = "wallstreetbets"
submissions = reddit.subreddit(subreddit_name).top(time_filter="day")
top_submission = next(s for s in submissions if not s.stickied)

tts.save_tts(
    top_submission.title + ". " + top_submission.selftext,
    "tts_audio/clip0.mp3",
)

# Capture screenshots of the Reddit data gathered
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(color_scheme="dark")
    page.set_viewport_size({"width": 900, "height": 1600})

    page.goto(REDDIT_URL + top_submission.permalink + "?sort=top")
    page.wait_for_load_state("networkidle")

    page.locator(f"#t3_{top_submission.id}").screenshot(path="screenshots/img0.png")

    top_submission.comment_sort = "top"
    i = 1
    for comment in islice((x for x in top_submission.comments if not x.stickied), 3):
        print(comment.body)
        tts.save_tts(comment.body, f"tts_audio/clip{i}.mp3")

        comment_locator = page.locator(f'[thingid=t1_{comment.id}]')
        comment_locator.scroll_into_view_if_needed()

        comment_bbox = comment_locator.bounding_box()
        next_reply_ypos = page.locator(f"#t1_{comment.id}-next-reply").bounding_box()["y"]
        page.screenshot(
            path=f"screenshots/img{i}.png",
            clip={**comment_bbox, "height": next_reply_ypos - comment_bbox["y"]}
        )
        i += 1

        # Screenshot & TTS for reply
        reply = comment.replies[0] if comment.replies else None
        print(f"Reply {i}:\n", reply.body)
        tts.save_tts(reply.body, f"tts_audio/clip{i}.mp3")

        try:
            next_reply_ypos = page.locator(f'#t1_{reply.id}-next-reply').bounding_box(timeout=1000)["y"]
        except PlaywrightTimeoutError:
            page.locator(f"faceplate-partial[slot=children-t1_{comment.id}-0]").click()
            next_reply_ypos = page.locator(f'#t1_{reply.id}-next-reply').bounding_box()["y"]
        page.screenshot(
            path=f"screenshots/img{i}.png",
            clip={**comment_bbox, "height": next_reply_ypos - comment_bbox["y"]},
        )
        i += 1

    
    browser.close()

