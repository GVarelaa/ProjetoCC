import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip = socket.gethostbyname("xubuncore")
print(ip)

s.bind(("127.0.0.1", 3333))

while True:
    msg, address = s.recvfrom(1024)
    print(msg.decode('utf-8'))

s.close()