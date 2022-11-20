# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 13/11/22
# Descrição: Criação de query e envio para o servidor
# Última atualização: Added comments

import socket
import sys
import random
from dns_message import *


def main():
    args = sys.argv
    args.pop(0)

    args_split = args[0].split(":")

    message_id = random.randint(1, 65535)
    ip_address = args_split[0]              # Address of the server
    #port = 6000                             # Default gate of the server
    port = args_split[1]
    domain_name = args[1]                   # Domain of the query (ex: mike.ggm.)
    type = args[2]                          # Type of entry (ex: A, NS)
    flags = "Q"

    if len(args_split) > 1:
        port = int(args_split[1])           # If port specified, update port

    if len(args) == 4 and args[3] == "R":   # If recursive mode enabled
        flags = "Q+R"

    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # Creation of a socket UDP

    query = DNSMessage(message_id, flags, domain_name, type)   # Creation of the query message

    socket_udp.sendto(query.to_string().encode('utf-8'), (ip_address, port))   # Sending of the query to the chosen server socket

    print(ip_address)
    print(port)

    message, address = socket_udp.recvfrom(1024)     # Blocks until response received
    message = message.decode('utf-8')



    sys.stdout.write(message)

    socket_udp.close()


if __name__ == "__main__" :
    main()