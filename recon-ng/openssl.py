from recon.core.module import BaseModule
from subprocess import check_output
from datetime import datetime
import re

class Module(BaseModule):

    meta = {
        'name': 'openssl Host Name Lookups',
        'author': 'laxa',
        'description': 'Uses the openssl to obtain host names from a site\'s SSL certificate metadata to update the \'hosts\' table.',
        'comments': (
            '',
        ),
        'query': 'SELECT DISTINCT ip_address FROM hosts WHERE ip_address IS NOT NULL',
    }

    def module_run(self, hosts):
        # build a regex that matches any of the stored domains
        domains = [x[0] for x in self.query('SELECT DISTINCT domain from domains WHERE domain IS NOT NULL')]
        regex = '(?:%s)' % ('|'.join(['\.'+re.escape(x)+'$' for x in domains]))
        for ip_address in hosts:
            self.heading(ip_address, level=0)
            try:
                output = check_output('openssl s_client -showcerts -connect {}:443 </dev/null 2>&1| openssl x509 -noout -text'.format(ip_address), shell=True)
            except:
                continue
            data = re.findall('(DNS:.*)', output)
            if len(data) == 0:
                continue
            for entry in data[0].split(','):
                host = entry.strip().rstrip()[4:] # remove the "DNS:" string
                if host.startswith('*.'):
                    continue
                self.add_hosts(host)
                self.output('Subject Alternative Names: \'%s\'' % host)
