#!/usr/bin/env python2

from subprocess import check_output, CalledProcessError
import requests
import re
import os

STATUS_FILE = '/home/laxa/Documents/up/status'
CREDENTIALS_FILE = '/home/laxa/scripts/.key'

def is_alive(server, t=1):
    if t > 3:
        return False
    cmd = '/bin/ping -c 2 %s' % server
    try:
        with open(os.devnull, 'w') as devnull:
            output = check_output(cmd.split(), stderr=devnull)
    except CalledProcessError:
        return is_alive(server, t + 1)
    except Exception as e:
        print(str(e))
        return False
    match = re.findall('(\d) received', output)
    if len(match) and int(match[0]) > 0:
        return True
    return False

def send_sms(message):
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            data = f.read()
        user, key = tuple(data.split())
        requests.get('https://smsapi.free-mobile.fr/sendmsg?user=%s&pass=%s&msg=%s' % (user, key, message))
    except Exception as e:
        print(str(e))

def boolean_to_status(status):
    return 'up' if status else 'down'

def main():
    # get status
    with open(STATUS_FILE, 'r') as f:
        servers = f.readlines()

    output = ''
    for server in servers:
        host, status = tuple(server.split())
        alive = is_alive(host)
        if not alive and status == 'up':
            msg = '%s went down' % host
            send_sms(msg)
            print(msg)
        elif alive and status == 'down':
            msg = '%s went up' % host
            send_sms(msg)
            print(msg)

        output += '%s %s\n' % (host, boolean_to_status(alive))

    # save status
    with open(STATUS_FILE, 'w') as f:
        f.write(output)

if __name__ == "__main__":
    main()
