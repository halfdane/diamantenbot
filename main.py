from reddit_front import RedditFront
import diamanten

if __name__ == "__main__":
    try:
        message = diamanten.create_message()
        print(message)

        RedditFront()#.postSuperstonkDaily(message)
    except Exception as e:
        print (str(e.__class__.__name__) + ": " + str(e))
