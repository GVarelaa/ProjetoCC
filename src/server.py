# Author: Guilherme Varela
# Created at: 30/10/22
# Last update: 03/11/12
# Description: Implements a server, a Primary Server
# Last update: Added basic structure
import socket
import sys
import threading

from log import Log
from database_parser import *
from query_message.message import parse_message, build_query_response, build_query_db_version_response, \
    build_query_init_transfer_response


class Server:
    def __init__(self, domain, default_domains, data_path, root_servers, log_path):
        self.mode = None
        self.domain = domain
        self.default_domains = default_domains
        self.log_path = log_path
        self.log = Log(log_path) # Objeto do tipo log
        self.root_servers = root_servers
        self.cache = parser_database(data_path)
        print(self.cache)

        # self.addresses_from = dict() estrutura para saber onde mandar a query com message id X

    def __str__(self):
        return f"Domínio: {self.domain}\nCache: {self.cache}\n" \
               f"Domínios por defeito: {self.default_domains}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log_file_path}"
    
    def __repr__(self):
        return f"Domínio: {self.domain}\nCache: {self.cache}\n" \
               f"Domínios por defeito: {self.default_domains}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log_file_path}"


    def parse_address(self, address):
        substrings = address.split(":")
        ip_address = substrings[0]

        if len(substrings) > 1:
            port = int(substrings[1])
        else:
            port = 5353 # porta default

        return (ip_address, port)

    def add_address(self, message, address):
        """
        Adiciona um endereço para onde a query com message id tem de retornar
        :param message_id: Message id da query
        :param address: Endereço a adicionar
        :return: void
        """
        (message_id, flags, name, type) = parse_message(message)
        self.addresses_from[message_id] = address

    def get_address(self, message):
        (message_id, flags, name, type) = parse_message(message)
        return self.addresses_from[message_id]

    def interpret_query(self, query): # interpret_query
        (message_id, flags, name, type) = parse_message(query)

        response_values = list()
        authorities_values = list()
        extra_values = list()

        if "T" in flags and self.domain == name: # Domínios são iguais (?)
            entries = count_file_entries(self.data_file_path)
            response = build_query_init_transfer_response(query, entries)

            return response

        elif "V" in flags:
            soaserial = self.cache.get_records_by_name_and_type(self.domain, "SOASERIAL")[0].value
            response = build_query_db_version_response(query, soaserial)

            return response

        elif "T" in flags:
            return query

        elif "R" in flags:
            return

        else:
            response_values = self.cache.get_records_by_name_and_type(name, type)

            if len(response_values) != 0:  # HIT
                authorities_values = self.cache.get_records_by_name_and_type(name, "NS")
                extra_values = list()

                for record in response_values:
                    records = self.cache.get_records_by_name_and_type(record.value, "A")
                    extra_values += records

                for record in authorities_values:
                    records = self.cache.get_records_by_name_and_type(record.value, "A")
                    extra_values += records

                response = build_query_response(query, response_values, authorities_values, extra_values)

                return response

            else:  # MISS
                return None

    def is_query(self, message):
        (message_id, flags, name, type) = parse_message(message)

        return "Q" in flags


def main():
    args = sys.argv
    config_filepath = args[1]
    port = args[2]
    timeout = args[3]
    mode = args[4]
    ip_address = '127.0.0.1'

    if not validate_port(port):
        return #adicionar log

    server = Server(config_filepath, mode)

    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # socket UDP
    socket_udp.bind((ip_address, int(port)))

    print(f"Estou à  escuta no {ip_address}:{port}")

    if server.server_type == "SP":
        threading.Thread(target=server.zone_transfer_sp).start()

    if server.server_type == "SS":
        threading.Thread(target=server.zone_transfer_caller_ss).start()

    while True:
        message, address_from = socket_udp.recvfrom(1024)
        message = message.decode('utf-8')

        print(f"Recebi uma mensagem do cliente {address_from}")

        is_query = server.is_query(message)

        server.log.log_qr(address_from, message)

        server.add_address(message, address_from)

        if is_query: # é query
            response = server.interpret_query(message)

            if response:
                socket_udp.sendto(response.encode('utf-8'), address_from)  # enviar para o destinatário
            else:
                return # MISS

        else: # é uma resposta a uma query
            socket_udp.sendto(message.encode('utf-8'), server.get_address(message))


    socket_udp.close()

if __name__ == "__main__" :
    main()

