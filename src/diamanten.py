from datetime import datetime
from pyquery import PyQuery as pq
import pytz
import logging
import re
import requests


def get_trade_gate_information():
    d = pq('https://www.tradegate.de/orderbuch.php?isin=US36467W1099')
    stueck__text = d('#stueck').text()
    stueck__text = re.sub('[^\d]', '', stueck__text)
    v = int(stueck__text)

    vol = \
        get_gettex_volume() + \
        get_ls_volume('https://www.ls-tc.de/de/aktie/gamestop-aktie') + \
        get_ls_volume('https://www.ls-x.de/de/aktie/gamestop-aktie') + \
        v

    return {
        'price': float(d('#last').text().replace(',', '.')),
        'volume': vol
    }


def get_ls_volume(url):
    d = pq(url)
    lines = d('tr [field="tradeTime"][decimals="2"]') \
        .filter(lambda i, this: re.match('[\d:]{8}.*?', pq(this).text())) \
        .parents('tr') \
        .find('[field="tradeSize"]').items()
    return sum([int(i.text()) for i in lines if i.text().isdigit()])


def get_gettex_volume():
    f = pq('https://www.gettex.de/suche/?tx_indexedsearch%5Bsword%5D=GS2C',
           headers={'user-agent': 'pyquery', 'cookie': 'cookie_optin=essential:1'})
    data_endpoint = f('#heading-timesSales').attr("data-ajax-uri")

    r = requests.get('https://www.gettex.de'+data_endpoint, headers={'user-agent': 'pyquery'})
    d = pq(r.json()["data"])
    volume = d('tbody tr:first td:last').text().replace('.', '')

    return int(volume)


def eur_to_usd():
    d = pq('https://www.onvista.de/devisen/Eurokurs-Euro-Dollar-EUR-USD')
    return float(d('.KURSDATEN span[data-push]').eq(0).text().replace(',', '.'))


def create_message(parsnip_url):
    ger = pytz.timezone('Europe/Berlin')
    nyse = pytz.timezone('America/New_York')

    now = datetime.now()
    tg = get_trade_gate_information()
    rate = eur_to_usd()

    message_parts = [
        "German market update (local time: %s) (nyse time: %s) " % (
        now.astimezone(ger).strftime("%T"), now.astimezone(nyse).strftime("%T")),
        "(generated by halfdane's [Diamantenbot](https://github.com/halfdane/diamantenbot))",
        "  ",
        "**$%.2f** ([€%.2f](https://www.tradegate.de/orderbuch.php?isin=US36467W1099)@" % (
        tg['price'] * rate, tg['price']),
        "[%.4f](https://www.onvista.de/devisen/Eurokurs-Euro-Dollar-EUR-USD)) " % rate,
        "**volume: %s** (" % (tg['volume']),
        "[TG](https://www.tradegate.de/orderbuch.php?isin=US36467W1099)+",
        "[LS-X](https://www.ls-x.de/de/aktie/gamestop-aktie)+",
        "[LS-TC](https://www.ls-tc.de/de/aktie/gamestop-aktie)+",
        "[GETTEX](https://www.gettex.de/suche/?tx_indexedsearch[sword]=GS2C)",
        ")",
        "  "
    ]

    if parsnip_url is not None:
        message_parts.append(parsnip_url)

    return '\n'.join(message_parts)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info(create_message(None))
