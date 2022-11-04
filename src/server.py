# Author: Guilherme Varela
# Created at: 30/10/22
# Last update: 03/11/12
# Description: Implements a server, a Primary Server
# Last update: Added basic structure

import socket
import sys

from parser import parser_df
from parser import parser_st
from parser import parser_cf
from query_message.message import *
class Server:
    def __init__(self, config_file_path):
        (d, d_fp, ps, ss, dd, rfp, lfp) = parser_cf(config_file_path)
        self.domain = d
        self.data_file_path = d_fp
        self.primary_server = ps    # caso de o servidor ser secundário
        self.secondary_servers = ss # caso de o servidor ser primário
        self.default_domains = dd
        self.root_servers_file_path = rfp
        self.log_file_path = lfp

        self.server_type = None   # if

        self.root_servers = parser_st(rfp)
        self.db = parser_df(d_fp)

    def __str__(self):
        return f"Domínio: {self.domain}\nBase de Dados Diretoria: {self.data_file_path}\nBase de Dados: {self.db}\nServidor primário: {self.primary_server}\nServidores secundários: {self.secondary_servers}\nDomínios por defeito: {self.default_domains}\nRoot Servers: {self.root_servers}\nFicheiro de Log: {self.log_file_path}"
    
    def __repr__(self):
        return f"Domínio: {self.domain}\nBase de Dados Diretoria: {self.data_file_path}\nBase de Dados: {self.db}\nServidor primário: {self.primary_server}\nServidores secundários: {self.secondary_servers}\nDomínios por defeito: {self.default_domains}\nRoot Servers: {self.root_servers}\nFicheiro de Log: {self.log_file_path}"


    def response_query(self, query): #objeto do tipo message
        (message_id, flags, name, type_of_value) = parse_message(query)

        response = ""

        if 'Q' in flags:
            response_values = self.db.get_values_by_type_and_parameter(type_of_value, name)
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

            if len(response_values) == 0:
                return None # caso em que contacta o primario se for secundario
            else:
                response = build_query_response(query, response_values, authorities_values, extra_values)

            return response



def main():
    args = sys.argv
    config_filepath = args[1]

    server = Server(config_filepath)
    print(server)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    endereco = '127.0.0.1'
    porta = 6000
    s.bind((endereco, porta))

    print(f"Estou à  escuta no {endereco}:{porta}")

    while True:
        msg, add = s.recvfrom(1024)
        msg = msg.decode('utf-8')

        server.response_query(msg)

        print(f"Recebi uma mensagem do cliente {add}")

    s.close()

if __name__ == "__main__" :
    main()

