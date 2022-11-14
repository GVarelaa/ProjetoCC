# Data de criação: 13/11/22
# Data da última atualização: 13/11/22
# Descrição: Receives queries for a given server
# Última atualização: Added comments
# TODO: Make it work for multiple servers
import socket
import threading
from dns import *
from parse.configuration_parser import *


def main():
    args = sys.argv
    config_path = args[1]       # Path of the config file of the server
    port = args[2]              # Port the server will be listening
    timeout = args[3]           # Time the server waits for a response
    mode = args[4]              # Debug enabled or disabled

    if not validate_port(port):
        return  # adicionar log

    server = parser_configuration(config_path, port, mode, threading.Lock())   # Parsing the config and database file, creating a server

    threading.Thread(target=server.zone_transfer).start()  # New thread for the zone transfer

    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           # Creation of the udp socket
    socket_udp.bind(("127.0.0.1", int(port)))                                # Binding to server ip

    while True:
        message, address_from = socket_udp.recvfrom(1024)                   # Receives a message

        threading.Thread(target=server.receive_queries, args=(message, address_from, socket_udp)).start()



    socket_udp.close()


if __name__ == "__main__":
    main()
