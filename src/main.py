from reddit_front import RedditFront
import diamanten
import sys, getopt
import time
import datetime
import pytz
import logging

SECONDS_PER_MIN = 60
ger = pytz.timezone('Europe/Berlin')


def its_time_to_run():
    # run every 5 minutes between 08:00 and 10:00 on weekdays
    start = datetime.time(8, 0)
    end = datetime.time(10, 0)
    now = datetime.datetime.now()

    too_early = now.astimezone(ger).time() < start
    too_late = now.astimezone(ger).time() > end

    rhythm_minute = now.minute % 10 == 0
    weekday = now.isoweekday() <= 5

    logging.info("It's now %s", now)

    if too_early:
        logging.info("  Too early")

    if too_late:
        logging.info("  Too late")

    if not rhythm_minute:
        logging.info("  not a 10 divisible minute")

    if not weekday:
        logging.info("  It's the weekend")

    return not too_early and not too_late and rhythm_minute and weekday


def main(argv):
    test = False
    try:
        opts, args = getopt.getopt(argv,"t")
    except getopt.GetoptError:
        logging.error('test.py [-t testrun]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-t':
            test = True

    reddit_front = RedditFront()

    while True:
        if its_time_to_run() or test:
            try:
                diamantenhaende_post = reddit_front.find_diamantenhaende_post()
                message = diamanten.create_message(diamantenhaende_post)
                logging.info(message)

                if not test:
                    reddit_front.post_superstonk_daily(message)
            except Exception as e:
                logging.error(str(e.__class__.__name__) + ": " + str(e), e)

        time.sleep(SECONDS_PER_MIN)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
