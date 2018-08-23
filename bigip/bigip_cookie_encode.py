from sys import argv, stdout, stderr, exit
from struct import pack, unpack
from socket import inet_aton

def encode_bigip_cookie(ipport):

        words = ipport.split(':')
        if len(words) != 2:
                stderr.write('error: expect format ip:port\n')
                return False

        ip = words[0]
        port = int(words[1])

        ip = unpack('<I', inet_aton(ip))[0]
        port = unpack('>H', pack('<H', port))[0]

        stdout.write('%s.%s.%s\n' % (ip, port, '0' * 4))

if __name__ == '__main__':

        if len(argv) < 2:
                stdout.write('usage: %s <ip:port> [ip:port...]\n' % (argv[0],))
                exit(1)

        for arg in argv[1:]:
                encode_bigip_cookie(arg)
