import praw

reddit = praw.Reddit(
    client_id="cRGrLMWPbuzyxJ45uu8tnw",
    client_secret="iCnan1uRpuo5OGA8RD20E6PSc56Y1g",
    user_agent="shorts-bot",
)

for submission in reddit.subreddit("test").hot(limit=10):
    print(submission.title)