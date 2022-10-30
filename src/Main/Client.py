# Author: Miguel Braga
# Created at: 29/10/22
# Last update: 29/10/12
# Description: 

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

msg = "Teste"

s.sendto(msg.encode('utf-8'), ('127.0.0.1', 3333))
