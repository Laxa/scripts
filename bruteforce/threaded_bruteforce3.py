#!/usr/bin/env python3

from queue import Queue
from threading import Thread
from itertools import product
import time
import requests
import sys
import re

requests.packages.urllib3.disable_warnings()

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
            except Exception as e:
                print(e)
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

def dostuff(auth):
    url = ''
    r = requests.get(url, verify=False)

def main():
    pool = ThreadPool(20)
    for _ in product('ABCDEFGHIJKLMNOPQRSTUVWXYZ', repeat=4):
        pool.add_task(dostuff, _)

    pool.wait_completion()

if __name__ == '__main__':
    main()
