#!/usr/bin/env python2

import sys
import re

bssid_reg = re.compile('(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}')

with open('dump-01.csv') as f:
    d = f.read()

AP = []
for line in d.split('\n'):
    s = line.rstrip().split(',')
    if len(s) == 0:
        continue
    if s[0] == 'Station MAC':
        break
    if not bssid_reg.match(s[0]):
        continue
    bssid, channel, authentication, beacons, essid = (s[0].strip(), s[3].strip(), s[5].strip(), s[9].strip(), s[13].strip())
    clients = []
    for client in d.split('\n'):
        if client.count(',') == 6 and client.split(',')[5].strip() == bssid:
            client = {'bssid':client.split(',')[0], 'power':client.split(',')[3], 'beacons':client.split(',')[4]}
            clients.append(client)
    new_ap = {'bssid':bssid, 'channel':channel, 'authentication':authentication, 'beacons':int(beacons), 'essid':essid, 'clients':clients}
    AP.append(new_ap)

newlist = sorted(AP, key=lambda k: k['beacons'], reverse=True)
for x in newlist:
    if x['authentication'] == 'OPN' or len(x['clients']) == 0:
        continue
    print x
