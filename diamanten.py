from datetime import datetime
import requests
from xml.etree import ElementTree
import pytz

def toFloat(input):
    if (type(input) == str):
        return float(input.replace(',', '.'))
    return input

def getTradegateInformation():
    r = requests.get('https://www.tradegate.de/refresh.php?isin=US36467W1099')
    return {
        'last': toFloat(r.json()["last"]),
        'stueck': toFloat(r.json()["stueck"]),
    }

def eurToUsd():
    r = requests.get('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml')
    root = ElementTree.fromstring(r.content)

    for child in root.iter('*'):
        if ('currency' in child.attrib.keys() and child.attrib['currency'] == 'USD'):
            return toFloat(child.attrib['rate'])

def create_message():
    ger = pytz.timezone('Europe/Berlin')
    nyse = pytz.timezone('America/New_York')

    now = datetime.now()
    tg = getTradegateInformation()
    rate = eurToUsd()

    return '\n'.join([
        "German market (Tradegate) update (local time: %s) (nyse time: %s)  " % (now.astimezone(ger).strftime("%T"), now.astimezone(nyse).strftime("%T")),
        "$%.2f (€%.2f @%.4f) (volume: %s)   " % (tg['last']*rate, tg['last'], rate, tg['stueck']),
        "",
        "Still trying to figure out how to post these on a regular basis, so this is posted in kinda random intervals"
    ])

