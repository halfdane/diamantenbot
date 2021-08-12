from reddit_front import RedditFront
import diamanten
import sys, getopt
import time
import datetime
import pytz

SECONDS_PER_MIN = 60
ger = pytz.timezone('Europe/Berlin')


def itsTimeToRun():
    # run every 5 minutes between 08:00 and 10:00 on weekdays
    start = datetime.time(8, 0)
    end = datetime.time(10, 0)
    now = datetime.datetime.now()

    morning = start <= now.astimezone(ger).time() <= end
    fifth_minute = now.minute % 10 == 0
    weekday = now.isoweekday() <= 5

    if not morning:
        print("It's not in the morning")

    if not fifth_minute:
        print("It's not in a 10 divisible minute")

    if not weekday:
        print("It's the weekend")

    return morning and fifth_minute and weekday


def main(argv):
    test = False
    try:
        opts, args = getopt.getopt(argv,"t")
    except getopt.GetoptError:
        print ('test.py [-t testrun]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-t':
            test = True

    reddit_front = RedditFront()

    while True:
        if itsTimeToRun():
            try:
                message = diamanten.create_message()
                print(message)

                if not test:
                    reddit_front.postSuperstonkDaily(message)
            except Exception as e:
                print(str(e.__class__.__name__) + ": " + str(e))

        time.sleep(SECONDS_PER_MIN)


if __name__ == "__main__":
    main(sys.argv[1:])
