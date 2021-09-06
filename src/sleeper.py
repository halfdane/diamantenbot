import time
import datetime
import pytz
import logging

ger = pytz.timezone('Europe/Berlin')


class Sleeper:
    stftime = "%x %X"
    market_open = datetime.time(hour=8, minute=0)
    market_close = datetime.time(hour=17, minute=30)

    def __init__(self, test=False):
        self.test = test

    def wait_for_next_diamanten(self, now=datetime.datetime.now()):
        logging.info("It's now %s" % now.strftime(self.stftime))

        too_early = now.astimezone(ger).time() < self.market_open
        too_late = now.astimezone(ger).time() > self.market_close
        not_tenth_minute = now.minute % 10 != 0
        sleep_until = None

        # if it's too late, whatever time it is:
        # market opens at 08:00 on the next weekday
        if too_late:
            sleep_until = self.__next_weekday_market_open(now)
            logging.info("it's too late. Sleeping until %s" % sleep_until.strftime(self.stftime))

        # if it's too early, sleep until market opens
        elif too_early:
            sleep_until = self.__next_weekday_market_open(now - datetime.timedelta(days=1))
            logging.info("it's too early. Sleeping until %s" % sleep_until.strftime(self.stftime))

        # if it's market time, sleep until the next tenth minute
        elif not_tenth_minute:
            tenth_minute = now.minute - (now.minute % 10) + 10
            sleep_until = now.replace(minute=tenth_minute % 60, second=0)

            if tenth_minute >= 60:
                sleep_until = sleep_until.replace(hour=sleep_until.hour + 1)

            logging.info("Not a tenth minute. Sleeping until %s" % sleep_until.strftime(self.stftime))

        if sleep_until is not None:
            self.__until(now, sleep_until)

        logging.info("It's time")

    def __next_weekday_market_open(self, now=datetime.datetime.now()):
        next_weekday = now + datetime.timedelta(days=7 - now.weekday() if now.weekday() > 3 else 1)
        return next_weekday.replace(hour=self.market_open.hour, minute=0, second=0, microsecond=0)

    def __until(self, now_1, target_time):
        end = target_time.timestamp()

        # Now we wait
        while True:
            now = now_1 if self.test else datetime.datetime.now()

            logging.info("It's now %s" % now.strftime(self.stftime))
            diff = end - now.timestamp()

            # Time is up!
            if diff <= 0:
                break
            else:
                # 'logarithmic' sleeping to minimize loop iterations
                seconds = diff / 2 if diff / 2 > 1 else 1
                logging.info("diff is %d sleeping for %d seconds" % (diff, seconds))
                if self.test:
                    now_1 = now_1 + datetime.timedelta(seconds=seconds)
                    time.sleep(1)
                else:
                    time.sleep(seconds)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    now = datetime.datetime(year=2021, month=9, day=6, hour=9, minute=57).astimezone(ger)
    logging.info(Sleeper(True).wait_for_next_diamanten(now))
