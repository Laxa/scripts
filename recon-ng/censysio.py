from recon.core.module import BaseModule
import time

class Module(BaseModule):

    meta = {
        'name': 'Censys.io Domain to hosts enumerator',
        'author': 'laxa',
        'description': 'Queries the censys.io API to find hosts based on domain.',
        'required_keys': ['censysio_id', 'censysio_secret'],
        'comments': (
            'Can also be used to target wildcard domains, to do so type:',
            'set source *.domain.tld',
        ),
        'query': 'SELECT DISTINCT domain FROM domains WHERE domain IS NOT NULL',
        'options': (
            ('rate', .2, True, 'search endpoint leak rate (tokens/second)'),
            ('limit', True, True, 'toggle rate limiting'),
        ),
    }

    def module_run(self, domains):
        for domain in domains:
            self.heading(domain, level=0)
            page = 1
            while True:
                resp = self._get_page(domain, page)
                if resp.status_code != 200:
                    self.error('Error: \'%s\'' % (resp.json.get('error')))
                    break
                self._load_results(resp)
                if resp.json.get('metadata').get('page') >= resp.json.get('metadata').get('pages'):
                    break
                self.verbose('Fetching the next page of results...')
                page += 1

    def _get_page(self, domain, page):
        payload = {
            'query': '443.https.tls.certificate.parsed.extensions.subject_alt_name.dns_names: \"{}\"'.format(domain),
            'page': page,
            'fields': ['ip', 'protocols']
        }
        resp = self.request(
            'https://censys.io/api/v1/search/ipv4',
            payload=payload,
            auth=(
                self.keys.get('censysio_id'),
                self.keys.get('censysio_secret')
            ),
            method='POST',
            content='JSON',
        )
        if self.options['limit']:
            time.sleep(1 / self.options['rate'])
        return resp

    def _load_results(self, resp):
        for result in resp.json.get('results'):
            ip_address = result.get('ip')
            for service in result.get('protocols'):
                port, protocol = service.split('/')
                self.add_ports(ip_address=ip_address, port=port, protocol=protocol)
