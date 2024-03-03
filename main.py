from itertools import islice
import praw

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


# Turn this Reddit information into audio clips using TTS

