import socket
import select
import sys

ports = [21, 22, 53, 25, 111, 443, 8443, 80, 8889, 10000, 21050, 48000, 48001, 14000]

def create_tcp_socket(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setblocking(0)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(10)
    return server_socket

def create_udp_socket(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setblocking(0)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    return server_socket

def main():
    ports

    tcp_list = []
    udp_list = []
    clients = []

    for port in ports:
        tcp_list.append(create_tcp_socket(port))
        udp_list.append(create_udp_socket(port))

    while True:
        read_list = clients + tcp_list + udp_list
        readable, writable, exceptional = select.select(read_list, [], read_list)
        for s in readable:
            if s in tcp_list:
                client_socket, address = s.accept()
                clients.append(client_socket)
            else:
                data = s.recv(1024)
                if data:
                    print data
                    if s in clients:
                        s.close()
                        clients.remove(s)

if __name__ == "__main__":
    main()
