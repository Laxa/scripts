from recon.core.module import BaseModule
from cookielib import CookieJar
from urlparse import urlparse
import urllib
import re
import time
import random

"""
Ceci est un module pour recon-ng. A placer dans recon-ng/modules/recon/hosts-hosts
"""

class Module(BaseModule):

    meta = {
        'name': 'Bing Web IP Neighbor Enumerator',
        'author': 'laxa',
        'description': 'Leverages the Bing Web and "ip:" advanced search operator to enumerate other virtual hosts sharing the same IP address. Updates the \'hosts\' table with the results.',
        'query': 'SELECT DISTINCT ip_address FROM hosts WHERE ip_address IS NOT NULL',
    }

    def module_run(self, addresses):
        base_url = 'https://www.bing.com/search'
        domains = [x[0] for x in self.query('SELECT DISTINCT domain from domains WHERE domain IS NOT NULL')]
        for address in addresses:
            self.heading(address, level=0)
            base_query = 'ip:' + address
            # control variables
            page = 0
            # results number per query on the page
            nr = 50
            total_results = 0
            subs = []
            cookiejar = CookieJar()
            cookiejar.set_cookie(self.make_cookie('SRCHHPGUSR', 'NEWWND=0&NRSLT=%d&SRCHLANG=&AS=1' % (nr), '.bing.com'))
            # execute search engine queries and scrape results storing subdomains in a list
            # loop until no new subdomains are found
            while True:
                content = None
                query = ''
                # build query based on results of previous results
                for sub in subs:
                    query += ' -domain:%s' % sub
                full_query = base_query + query
                url = '%s?first=%d&q=%s' % (base_url, (total_results), urllib.quote_plus(full_query))
                # bing errors out at > 2059 characters not including the protocol
                if len(url) > 2066:
                    self.alert('Url is too long cant harvest everything for this IP...')
                self.verbose('URL: %s' % (url))
                # send query to search engine
                resp = self.request(url, cookiejar=cookiejar)
                if resp.status_code != 200:
                    self.alert('Bing has encountered an error. Please submit an issue for debugging.')
                    break
                content = resp.text
                with open('debug', 'w') as f:
                    f.write(content.encode('utf-8'))
                sites = re.findall('b_algo\">(?:<div class=\"b_title\">)?<h2><a href=\"([^\"]+)', content)
                self.verbose(sites)
                # create a unique list
                sites = list(set(sites))
                self.verbose('Got %d results' % len(sites))
                for site in sites:
                    stripped_site = '{uri.netloc}'.format(uri = urlparse(site))
                    self.verbose(stripped_site)
                    if stripped_site not in subs:
                        subs.append(stripped_site)
                    if stripped_site not in domains:
                        self.add_hosts(stripped_site, address)
                # This stuff is actually fucked up because french version, cookies may have changed
                # Beware that this could break
                # We use the query builder to avoid having pages so it should'nt matter that much in the end
                if '>Next</a>' and 'Page suivante' not in content:
                    break
                else:
                    page += 1
                total_results += len(sites)
                # sleep script to avoid lock-out
                self.verbose('Sleeping to avoid lockout...')
                time.sleep(random.randint(5, 15))
