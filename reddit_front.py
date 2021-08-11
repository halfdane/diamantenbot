import praw
import os

class RedditFront:

    def __init__(self):
        user_agent = "desktop:com.halfdane.diamanten_bot:v0.0.1 (by u/half_dane)"
        print("Logging in..")
        try:
            self.reddit = praw.Reddit(username=os.environ["reddit_username"],
                            password=os.environ["reddit_password"],
                            client_id=os.environ["client_id"],
                            client_secret=os.environ["client_secret"],
                            user_agent=user_agent)

            print("Logged in!")
        except:
            print("Failed to log in!")

    def postSuperstonkDaily(self, message):
        subreddit = self.reddit.subreddit("Superstonk")
        expectedName = "$GME Daily Discussion Thread"
        for submission in subreddit.hot(limit=10):
            if (submission.title == expectedName):
                submission.reply(message)

