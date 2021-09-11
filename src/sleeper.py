import time
import datetime
import pytz
import logging

ger = pytz.timezone('Europe/Berlin')


class Sleeper:
    stftime = "%x %X"
    market_open = datetime.time(hour=8, minute=0)
    market_close = datetime.time(hour=10, minute=00)

    def __init__(self, test=False):
        self.test = test

    def wait_for_next_diamanten(self, timestamp=None):
        now = datetime.datetime.now() if timestamp is None else timestamp

        self.__debug_datetime("It's now %s", now)

        no_tradingday = now.astimezone(ger).now.weekday() > 4
        too_early = now.astimezone(ger).time() < self.market_open
        too_late = now.astimezone(ger).time() > self.market_close
        not_tenth_minute = now.minute % 10 != 0
        sleep_until = None

        if no_tradingday:
            sleep_until = self.__next_weekday_market_open(now)
            self.__debug_datetime("it's not a tradingday. Sleeping until %s", sleep_until, logging.info)

        # if it's too late, whatever time it is:
        # market opens at 08:00 on the next weekday
        elif too_late:
            sleep_until = self.__next_weekday_market_open(now)
            self.__debug_datetime("it's too late. Sleeping until %s", sleep_until, logging.info)

        # if it's too early, sleep until market opens
        elif too_early:
            sleep_until = self.__next_weekday_market_open(now - datetime.timedelta(days=1))
            self.__debug_datetime("it's too early. Sleeping until %s", sleep_until, logging.info)

        # if it's market time, sleep until the next tenth minute
        elif not_tenth_minute:
            tenth_minute = now.minute - (now.minute % 10) + 10
            sleep_until = now.replace(minute=tenth_minute % 60, second=0)

            if tenth_minute >= 60:
                sleep_until = sleep_until.replace(hour=sleep_until.hour + 1)

            self.__debug_datetime("Not a tenth minute. Sleeping until %s", sleep_until, logging.info)

        if sleep_until is not None:
            self.__until(now, sleep_until)

        logging.info("It's time")

    def __next_weekday_market_open(self, timestamp=None):
        now = datetime.datetime.now() if timestamp is None else timestamp
        next_weekday = now + datetime.timedelta(days=7 - now.weekday() if now.weekday() > 3 else 1)
        return next_weekday.astimezone(ger).replace(hour=self.market_open.hour, minute=0, second=0, microsecond=0)

    def __until(self, now, target_time):
        end = target_time.timestamp()

        self.__debug_datetime("Not doing much until %s", target_time, logging.info)
        self.__debug_datetime("It's now %s", now, logging.info)

        # Now we wait
        while True:
            now = datetime.datetime.now() if not self.test else now

            self.__debug_datetime("It's now %s", now)
            diff = end - now.timestamp()

            # Time is up!
            if diff < 0:
                logging.info("The difference is %f" % diff)
                break

            # 'logarithmic' sleeping
            half_diff = diff / 2
            logging.debug("%fs to go. Sleeping for %fs." % (diff, half_diff))
            if not self.test:
                time.sleep(half_diff)
            else:
                now = now + datetime.timedelta(seconds=half_diff)
                time.sleep(half_diff if half_diff <= 1 else 1)

            if diff <= 0.1:
                logging.debug("The difference is %f" % diff)
                break

    def __debug_datetime(self, string, dt, logfunction=logging.debug):
        logfunction(string % dt.astimezone(ger).strftime(self.stftime))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    astimezone = datetime.datetime(year=2021, month=9, day=6, hour=9, minute=57)
    logging.info(Sleeper(True).wait_for_next_diamanten(astimezone))
