import socket

IP = 'x.x.x.x'
MESSAGE = 'Hello, World!\n'
DEBUG = True
ports = [21, 22, 53, 25, 111, 443, 8443, 80, 8889, 10000, 21050, 48000, 48001, 14000]
socket.setdefaulttimeout(5)

print('Testing UDP')
# UDP
for port in ports:
    try:
        sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
        sock.sendto(MESSAGE.encode(), (IP, port))
    except Exception as e:
        print(e)

# TCP
print('Testing TCP')
for port in ports:
    try:
        sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_STREAM) # TCP
        sock.connect((IP, port))
        sock.send(MESSAGE.encode())
        print('Port %d working' % port)
    except socket.timeout:
        if DEBUG:
            print('Port %d timeout' % port)
        pass
    except Exception as e:
        print(e)
