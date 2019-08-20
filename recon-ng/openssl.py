from recon.core.module import BaseModule
from recon.mixins.threads import ThreadingMixin
from subprocess import Popen, DEVNULL, STDOUT, PIPE
from datetime import datetime
import sys
import re

class Module(BaseModule, ThreadingMixin):

    meta = {
        'name': 'openssl Host Name Lookups',
        'author': 'laxa (@l4x4)',
        'description': 'Uses the openssl to obtain host names from a site\'s SSL certificate metadata to update the \'hosts\' table.',
        'version': '1.0',
        'query': 'SELECT DISTINCT ip_address FROM hosts WHERE ip_address IS NOT NULL',
        'comments': (
            'Will possibly have duplicates, remove them with `db query delete from hosts where rowid not in (select min(rowid) from hosts group by host)`',
        ),
        'options': (
            ('timeout', 1, False, 'Timeout for the openssl client connection'),
            ('port', 443, False, 'Port to initiate SSL connection to'),
        ),
    }

    def module_run(self, hosts):
        self.thread(hosts)
    
    def module_thread(self, ip_address):
        self.heading(ip_address, level=0)
        try:
            p1 = Popen(('timeout %s openssl s_client -showcerts -connect %s:%s' % (str(self.options['timeout']), ip_address, str(self.options['port']))).split(),
                stdin=DEVNULL, stderr=STDOUT, stdout=PIPE)
            p2 = Popen('openssl x509 -noout -text'.split(), stdin=p1.stdout, stdout=PIPE)
            output = p2.communicate()[0]
        except:
            return
        data = re.findall('(DNS:.*)', output.decode(sys.stdout.encoding))
        if len(data) == 0:
            return
        for entry in data[0].split(','):
            host = entry.strip().rstrip()[4:] # remove the "DNS:" string
            if host.startswith('*.'):
                host = host[2:]
            self.insert_hosts(host)
            self.output('Subject Alternative Names: \'%s\'' % host)
