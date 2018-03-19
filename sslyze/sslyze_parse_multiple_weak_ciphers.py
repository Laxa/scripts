#!/usr/bin/env python2

import os
import re

files = os.listdir('.')

blacklist = ['DES', 'RC4', 'DH-1024', 'MD5']
bad_ciphers = []
servers = []

for f in files:
    if f.startswith('sslyze_') and f.endswith('.txt'):
        with open(f, 'r') as tmp:
            data = tmp.readlines()
        m = re.findall('sslyze_(.+?)\.txt', f)
        server = m[0].replace('_', ':')
        m = re.findall('10\.(?:\d{1,3}\.){2}\d{1,3}', ''.join(data))
        if len(m) == 0:
            continue
        server += ' (%s)' % m[0]
        for line in data:
            for bad in blacklist:
                cipher = ''
                if line.find(bad) != -1:
                    cipher = line.split()[0]
                    if server not in servers:
                        servers.append(server)
                if line.find('1024') != -1 and len(cipher) > 0:
                    cipher += ' with DH-1024'
                if len(cipher) > 0 and cipher not in bad_ciphers:
                    bad_ciphers.append(cipher)

for server in servers:
    print server
for cipher in bad_ciphers:
    print cipher
