from datetime import datetime
from pyquery import PyQuery as pq
import logging
import re
import requests


def convert_int(s):
    return int(s) if s and s.isdecimal() else 0

def convert_float(s):
    return float(s) if s and s.isdecimal() else 0.0


def get_trade_gate_information():
    d = pq('https://www.tradegate.de/orderbuch.php?isin=US36467W1099')
    stueck__text = d('#stueck').text()
    stueck__text = re.sub('[^\d]', '', stueck__text)
    v = convert_float(stueck__text)

    return {
        'price': float(d('#last').text().replace(',', '.')),
        'volume': v
    }


def get_ls_volume(url):
    d = pq(url)
    lines = d('tr [field="tradeTime"][decimals="2"]') \
        .filter(lambda i, this: re.match('[\d:]{8}.*?', pq(this).text())) \
        .parents('tr') \
        .find('[field="tradeSize"]').items()
    return sum([convert_int(i.text()) for i in lines])


def get_gettex_volume():
    f = pq('https://www.gettex.de/suche/?tx_indexedsearch%5Bsword%5D=GS2C',
           headers={'user-agent': 'pyquery', 'cookie': 'cookie_optin=essential:1'})
    data_endpoint = f('#heading-timesSales').attr("data-ajax-uri")

    r = requests.get('https://www.gettex.de' + data_endpoint, headers={'user-agent': 'pyquery'})
    d = pq(r.json()["data"])
    volume = d('tbody tr:first td:last').text().replace('.', '')

    return convert_int(volume)


def eur_to_usd():
    d = pq('https://www.onvista.de/devisen/Eurokurs-Euro-Dollar-EUR-USD')
    return float(d('.KURSDATEN span[data-push]').eq(0).text().replace(',', '.'))


def get_diamanten_data():
    tg = get_trade_gate_information()
    rate = eur_to_usd()

    return {
        'now': datetime.now(),
        'euro2usd': rate,
        'price': tg['price'],
        'sources': [
            {
                'name': 'TradeGate', 'short_name': 'TG',
                'link': 'https://www.tradegate.de/orderbuch.php?isin=US36467W1099',
                'volume': tg['volume']
            },
            {
                'name': 'Lang&Schwarz Exchange', 'short_name': 'LS-X',
                'link': 'https://www.ls-x.de/de/aktie/gamestop-aktie',
                'volume': get_ls_volume('https://www.ls-x.de/de/aktie/gamestop-aktie')
            },
            {
                'name': 'Lang&Schwarz Tradecenter', 'short_name': 'LS-TC',
                'link': 'https://www.ls-tc.de/de/aktie/gamestop-aktie',
                'volume': get_ls_volume('https://www.ls-tc.de/de/aktie/gamestop-aktie')
            },
            {
                'name': 'gettex', 'short_name': 'gettex',
                'link': 'https://www.gettex.de/suche/?tx_indexedsearch[sword]=GS2C',
                'volume': get_gettex_volume()
            }
        ],
        'created_by': "halfdane's [Diamantenbot](https://github.com/halfdane/diamantenbot)"
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info(get_diamanten_data())
