# Author: Gabriela Cunha, Guilherme Varela and Miguel Braga
# Created at: 11/11/22
# Last update date: 11/11/22
# Description: Module that implements the main server that receives and forwards dns messages to each of the servers
# Last update: Added documentation

import sys
import threading
import string
from queries import dns
from parse.configuration_parser import *


def main():
    # Read command-line arguments
    args = sys.argv

    i = 1
    config_files = [] # List of config files of each server

    while not args[i].isnumeric():
        config_files.append(args[i])
        i = i+1

    port = args[i]
    timeout = args[i+1] # TTL
    mode = args[i+2] # Debug or not

    ip_address = '127.0.0.1'

    if not validate_port(port):
        print("")# TODO Add log

    # Parsing of all server files
    # TODO - change to dictionary
    servers = []
    for config_path in config_files:
        servers.append(parser_configuration(config_path))

    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket UDP shared by all servers
    socket_udp.bind((ip_address, int(port)))

    socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"Estou à escuta no {ip_address}:{port}")

    threading.Thread(target=servers[0].zone_transfer(socket_tcp)).start() # Only one server for now

    while True:
        message, address_from = socket_udp.recvfrom(1024)

        print(f"Recebi uma mensagem do cliente {address_from}")

        query = dns.string_to_dns(message.decode('utf-8')) # Conversion back to dns PDU
        #server.log.log_qr(address_from, message)

        if "Q" in query.flags:  # é queries
            response = servers[0].interpret_query(query) # objeto DNS

            if "A" in response.flags:
                socket_udp.sendto(response.dns_to_string().encode('utf-8'), address_from)  # enviar para o destinatário
            else:
                return  # MISS

        else:  # é uma resposta a uma queries
            socket_udp.sendto(query.dns_to_string().encode('utf-8'), servers[0].get_address(message))


    socket_udp.close()


if __name__ == "__main__":
    main()

