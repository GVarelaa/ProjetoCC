# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 13/11/22
# Data da última atualização: 13/11/22
# Descrição: Receives queries for a given server
# Última atualização: Added comments
# TODO: Make it work for multiple servers

import sys
import threading
from parse.configuration_parser import *
from queries.dns import *


def main():
    args = sys.argv
    config_path = args[1]       # Path of the config file of the server
    port = args[2]              # Port the server will be listening
    timeout = args[3]           # Time the server waits for a response
    mode = args[4]              # Debug enabled or disabled

    if not validate_port(port):
        return  # adicionar log

    server = parser_configuration(config_path, mode)                        # Parsing the config and database file, creating a server
    

    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)           # Creation of the udp socket
    ip_address = ""                                                         # Default ip
    socket_udp.bind((ip_address, int(port)))                                # Binding to server ip

    threading.Thread(target=server.zone_transfer).start()                   # New thread for the zone transfer

    #print(f"Estou à  escuta no {ip_address}:{port}")

    while True:
        message, address_from = socket_udp.recvfrom(1024)                   # Receives a message

        print(f"Recebi uma mensagem do cliente {address_from}")

        query = string_to_dns(message.decode('utf-8'))                      # Decodes and converts to PDU
        #server.log.log_qr(address_from, message) corrigir

        if "Q" in query.flags:                                                                          # It is a query
            response = server.interpret_query(query)                                                    # Create a response to that query

            if "A" in response.flags:                                                                   # Answer in cache/DB
                socket_udp.sendto(response.query_to_string().encode('utf-8'), address_from)             # Send it back
            else:       
                return                                                                                  # MISS

        else:                                                                                           # It's a response to a query
            socket_udp.sendto(query.query_to_string().encode('utf-8'), server.get_address(message))     


    socket_udp.close()


if __name__ == "__main__":
    main()