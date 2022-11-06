# Author: Guilherme Varela
# Created at: 30/10/22
# Last update: 03/11/12
# Description: Implements a server, a Primary Server
# Last update: Added basic structure
import json
import socket
import sys
import threading

from parser import *
from query_message.message import *
class Server:
    def __init__(self, config_file_path, mode):
        (d, d_fp, ps, ss, dd, rfp, lfp) = parser_cf(config_file_path)
        self.mode = mode
        self.domain = d
        self.data_file_path = d_fp
        self.primary_server = ps
        self.secondary_servers = ss
        self.default_domains = dd
        self.root_servers_file_path = rfp
        self.log_file_path = lfp

        if self.primary_server is None:
            self.server_type = "SP"
        elif len(self.secondary_servers) == 0:
            self.server_type = "SS"
        else:
            self.server_type = "SR"

        self.root_servers = parser_st(rfp)
        self.db = parser_df(d_fp)
        self.addresses_from = dict() #estrutura para saber onde mandar a query com message id X

    def __str__(self):
        return f"Domínio: {self.domain}\nBase de Dados Diretoria: {self.data_file_path}\nBase de Dados: {self.db}\n" \
               f"Servidor primário: {self.primary_server}\nServidores secundários: {self.secondary_servers}\n" \
               f"Domínios por defeito: {self.default_domains}\nTipo do servidor: {self.server_type}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log_file_path}"
    
    def __repr__(self):
        return f"Domínio: {self.domain}\nBase de Dados Diretoria: {self.data_file_path}\nBase de Dados: {self.db}\n" \
               f"Servidor primário: {self.primary_server}\nServidores secundários: {self.secondary_servers}\n" \
               f"Domínios por defeito: {self.default_domains}\nTipo do servidor: {self.server_type}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log_file_path}"

    def zone_transfer_sp(self):
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket TCP
        socket_tcp.bind(("127.0.0.1", 6500))
        socket_tcp.listen()

        while True:
            connection, address = socket_tcp.accept()

            msg = connection.recv(1024)

            if not msg:
                break

            msg = msg.decode('utf-8')
            # invocar interpret query
            print(msg)

            if msg == "zone transfer":
                connection.sendall(str(self.db.dict).encode('utf-8'))
            connection.close()

    def zone_transfer_ss(self):
        sp = self.primary_server

        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        (ip_address, port) = self.parse_address(self.primary_server)

        socket_tcp.connect((ip_address, port))

        print(f"Estou à escuta no {ip_address}:{port}")

        msg = build_message(self.domain, "", "Q+T") # Construir query para pedir transferencia de zona

        socket_tcp.sendall(msg.encode('utf-8'))

        b = b'' # Iniciar  com 0 bytes
        while True:
            tmp = socket_tcp.recv(1024)

            if not tmp:
                break

            msg = tmp.decode('utf-8')

            b += tmp

        db = b.decode('utf-8')
        print(db)


    def parse_address(self, address):
        substrings = address.split(";")
        ip_address = substrings[0]

        if len(substrings) > 1:
            port = int(substrings[1])
        else:
            port = 5353 # porta default

        return (ip_address, port)

    def add_address(self, message_id, address):
        """
        Adiciona um endereço para onde a query com message id tem de retornar
        :param message_id: Message id da query
        :param address: Endereço a adicionar
        :return: void
        """
        self.addresses_from[message_id] = address

    def get_address(self, message_id):
        return self.addresses_from[message_id]

    def response_query(self, query): # interpret_query
        (message_id, flags, name, type_of_value) = parse_message(query)
        response_values = self.db.get_values_by_type_and_parameter(type_of_value, name)

        if len(response_values) != 0:     # HIT
            authorities_values = self.db.get_values_by_type_and_parameter("NS", name)
            extra_values = list()

            for data_entry in response_values:
                if data_entry.value in self.db.get_parameter_keys("A"):
                    extra_values += self.db.get_values_by_type_and_parameter("A", data_entry.value)
            for data_entry in authorities_values:
                if data_entry.value in self.db.get_parameter_keys("A"):
                    extra_values += self.db.get_values_by_type_and_parameter("A", data_entry.value)

            response = build_query_response(query, response_values, authorities_values, extra_values)

            return response

        else:   # MISS
            return None


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
    #print(server)

    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # socket UDP
    socket_udp.bind((ip_address, int(port)))

    if server.server_type == "SP":
        threading.Thread(target=server.zone_transfer_sp).start()

    if server.server_type == "SS":
        threading.Thread(target=server.zone_transfer_ss).start()

    print(f"Estou à  escuta no {ip_address}:{port}")

    while True:
        msg, address_from = socket_udp.recvfrom(1024)
        msg = msg.decode('utf-8')

        (message_id, flags, name, type_of_value) = parse_message(msg)

        server.add_address(message_id, address_from)

        if "Q" in flags: # é uma query
            response = server.response_query(msg)

            if response is not None:
                socket_udp.sendto(response.encode('utf-8'), address_from) # enviar para o destinatário
            else: #miss
                return

        else: # é uma reposta duma query e temos de mandar de volta
            socket_udp.sendto(msg.encode('utf-8'), server.get_address(message_id)) # enviar para o destinatário

        print(f"Recebi uma mensagem do cliente {address_from}")

    socket_udp.close()

if __name__ == "__main__" :
    main()

