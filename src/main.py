from reddit_front import RedditFront
from sleeper import Sleeper
import diamanten
import comment

import sys, getopt
import datetime
import logging


def main(argv):
    test = False
    try:
        opts, args = getopt.getopt(argv, "t")
    except getopt.GetoptError:
        logging.error('test.py [-t testrun]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-t':
            test = True

    reddit_front = RedditFront()
    sleeper = Sleeper(test)

    while True:
        sleeper.wait_for_next_diamanten(datetime.datetime.now())

        try:
            diamantenhaende_post = reddit_front.find_diamantenhaende_post()
            diamanten_data = diamanten.get_diamanten_data()
            message = comment.create_message(diamantenhaende_post, diamanten_data)
            logging.info("\n%s" % message)

            if test:
                exit()

            reddit_front.post_superstonk_daily(message)
        except Exception as e:
            logging.error(str(e.__class__.__name__) + ": " + str(e), e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
