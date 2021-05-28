#!/usr/bin/env python3

import requests
import datetime
import json
import html
import time
import sys
import re

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = 'https://www.boursorama.com'
MAX_TRIES = 3
ERROR_DELAY = 30
# proxies = dict(https='http://127.0.0.1:8080')
proxies = False
debug = False

wallet = []]

# Verify day and exit if bourse not open
day = datetime.datetime.today().weekday()

# If not monday to friday, bourse is closed
if day not in [0, 1, 2, 3, 4] and not debug:
    sys.exit()

total = 0
total_cost = 0
for stock in wallet:
    url = '{}/cours/{}/'.format(URL, stock['endpoint'])
    cur_try = 1
    while cur_try < MAX_TRIES:
        r = requests.get(url, proxies=proxies, verify=False)
        if r.status_code == 200:
            break
        cur_try += 1
        time.sleep(ERROR_DELAY)

    data = html.unescape(r.text)
    regex = '(\{\"symbol\":\"%s\"[^\}]+\})' % stock['endpoint']
    match = re.findall(regex, data)
    scrap_data = json.loads(match[0])
    current_price = scrap_data['last']

    total += current_price * stock['q']
    total_cost += stock['b'] * (stock['q'] - stock['bonus'])

    match = re.findall('<span class="u-color-stream-(?:down|up)"><span class="c-instrument c-instrument--variation" data-ist-variation>([^<]*)', data)
    current_percent = match[0].strip().rstrip()[:-1]

    match = re.findall('<td class=\"c-table__cell c-table__cell--dotted c-table__cell[^\"]*">.+?(-?\d{1,3}\.\d{1,3}%).+?</td>', data, re.DOTALL)
    week_percent, month_percent, year_percent = 0, 0, 0
    try:
        week_percent = float(match[4].strip().rstrip()[:-1])
        month_percent = float(match[5].strip().rstrip()[:-1])
        sixmonth_percent = float(match[7].strip().rstrip()[:-1])
        year_percent = float(match[8].strip().rstrip()[:-1])
    except:
        pass

    base_price = stock['b']
    q = stock['q']
    try:
        percent_win = ((current_price - base_price) / base_price) * 100
    except ZeroDivisionError:
        percent_win = 0

    text = '{} {} {}% gain par rapport achat {} ({}%)'.format(stock['name'],
        str(current_price),
        str(current_percent),
        str(round((current_price * q) - (q * base_price), 2)),
        str(round(percent_win, 2)))
    text += '\nResultat semaine: {}%, 1 mois: {}%, 6 mois: {} %, 1 annnee: {}%'.format(str(week_percent),
            str(month_percent), str(sixmonth_percent), str(year_percent))

    print(text)

gain = ((total - total_cost) / total_cost) * 100
text = 'Investi: {}, Valeur: {}, Gain: {}%'.format(str(round(total_cost, 2)),
    str(round(total, 2)),
    str(round(gain, 2)))

print(text)
