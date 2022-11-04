# Author: Guilherme Varela
# Created at: 30/10/22
# Last update: 03/11/12
# Description: Implements a server, a Primary Server
# Last update: Added basic structure

import socket
import sys

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


    def response_query(self, query): #objeto do tipo message
        (message_id, flags, name, type_of_value) = parse_message(query)

        response = ""

        if 'Q' in flags:
            response_values = self.db.get_values_by_type_and_parameter(type_of_value, name)

            if len(response_values) != 0:     # HIT
                authorities_values = self.db.get_values_by_type_and_parameter("NS", name)
                extra_values = list()

                for data_entry in response_values:
                    if data_entry.value in self.db.get_parameter_keys("A"):
                        for de in self.db.get_values_by_type_and_parameter("A", data_entry.value):
                            extra_values.append((de, data_entry.value))

                for data_entry in authorities_values:
                    if data_entry.value in self.db.get_parameter_keys("A"):
                        for de in self.db.get_values_by_type_and_parameter("A", data_entry.value):
                            extra_values.append((de, data_entry.value))

                response = build_query_response(query, response_values, authorities_values, extra_values)

                return (True, response)

            else:   # SS
                if self.server_type == "SS":
                    return (False, self.primary_server) # Caso não encontra, devolve a query original e o ip para onde tem de mandar a query


def main():
    args = sys.argv
    config_filepath = args[1]
    port = args[2]
    timeout = args[3]
    mode = args[4]

    if not validate_port(port):
        return #adicionar log

    server = Server(config_filepath, mode)
    print(server)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    ip_address = '127.0.0.1'
    s.bind((ip_address, port))

    print(f"Estou à  escuta no {ip_address}:{port}")

    while True:
        msg, address_from = s.recvfrom(1024)
        msg = msg.decode('utf-8')

        (bool, string) = server.response_query(msg)

        if bool == False: # Se falhar no acesso à base de dados, reenvia para o seu servidor primario
            substrings = string.split(":")
            address = substrings[0]
            if len(substrings) > 1:
                port = substrings[1]

            s.sendto(msg.encode('utf-8'), (address, port))

        else:
            s.sendto(string.encode('utf-8'), address_from) # Deu hit e envia a resposta para o endereço de onde veio


        print(f"Recebi uma mensagem do cliente {address_from}")

    s.close()

if __name__ == "__main__" :
    main()

