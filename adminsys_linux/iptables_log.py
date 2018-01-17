#!/usr/bin/env python2

'''
Script that checks the OUTPUT:DROP in iptables and gather the associated events
in syslog to output them
Best used with crontab:
*/30 * * * * /usr/bin/python /root/iptables_log.py
Also need to create file COUNT_FILE with a number inside it
'''

import subprocess, sys, os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

CMD = 'iptables -vL OUTPUT'
COUNT_FILE = 'last_dump_size'

output = subprocess.check_output(CMD.split())
dump_log_size = int(output.split('\n')[len(output.split('\n')) - 2].split()[0])

with open(COUNT_FILE, 'r') as f:
    prev_size = int(f.read())

if dump_log_size > prev_size:
    drop_log = []
    syslog = open('/var/log/syslog', 'r')
    lines = syslog.readlines()
    syslog.close()
    for log in lines:
        if log.find('OUTPUT:DROP') != -1:
            drop_log.append(log.rstrip())
else:
    with open(COUNT_FILE, 'w') as f:
        f.write(str(dump_log_size))
    sys.exit()

output = ''
i = 0
index = len(drop_log) - 1
while i < dump_log_size - prev_size:
    output += drop_log[index] + '\n'
    i += 1
    index -= 1

print output.rstrip()
with open(COUNT_FILE, 'w') as f:
    f.write(str(dump_log_size))
