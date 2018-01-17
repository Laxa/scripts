#!/usr/bin/env python2

'''
Script that checks syslog and output when bad words are encountered
Kind of a mini SIEM targeted on memory corruption exploited that makes process
crash
Script is intended to be run with crontab:
* * * * * /usr/bin/python /root/error.py
'''

import os.path

os.chdir(os.path.dirname(os.path.realpath(__file__)))

with open('/var/log/syslog', 'r') as f:
    d = f.readlines()
with open('last', 'r') as f:
    last = f.read()

triggerWords = ['segfault', 'sigill', 'trap', 'general protection', 'invalid opcode']

if last in d:
    for line in xrange(d.index(last) + 1, len(d)):
        if any([x in d[line] for x in triggerWords]):
            print d[line].rstrip()
else:
    for line in d:
        if any([x in line for x in triggerWords]):
            print line.rstrip()

with open('last', 'w') as f:
    f.write(d[len(d) - 1])
