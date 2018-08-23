from sys import argv, stdout, stderr, exit
from struct import pack, unpack
from socket import inet_ntoa

def decode_bigip_cookie(cookie):

	words = cookie.split('.')
	if len(words) != 3:
		stderr.write('error: expect format a.b.c\n')
		return False

	ip = int(words[0], 10)
	port = int(words[1], 10)

	ip = inet_ntoa(pack('<I', ip))
	port = unpack('>H', pack('<H', port))[0]

	stdout.write('%s -> %s:%i\n' % (cookie, ip, port))

if __name__ == '__main__':
	
	if len(argv) < 2:
		stdout.write('usage: %s <cookie> [cookie2..]\n' % (argv[0],))
		exit(1)

	for arg in argv[1:]:
		decode_bigip_cookie(arg)
		
