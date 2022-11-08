# Author: Guilherme Varela
# Created at: 30/10/22
# Last update: 03/11/12
# Description: Implements a server, a Primary Server
# Last update: Added basic structure
import socket
import sys
import threading

from time import sleep
from parser import *
from query_message.message import *
from log import *

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
        self.log = Log(lfp) # Objeto do tipo log

        if self.primary_server is None:
            self.server_type = "SP"
        elif len(self.secondary_servers) == 0:
            self.server_type = "SS"
        else:
            self.server_type = "SR"

        self.root_servers = parser_st(rfp)
        self.cache = parser_df(d_fp)
        self.addresses_from = dict() #estrutura para saber onde mandar a query com message id X

    def __str__(self):
        return f"Domínio: {self.domain}\nBase de Dados Diretoria: {self.data_file_path}\nBase de Dados: {self.cache}\n" \
               f"Servidor primário: {self.primary_server}\nServidores secundários: {self.secondary_servers}\n" \
               f"Domínios por defeito: {self.default_domains}\nTipo do servidor: {self.server_type}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log_file_path}"
    
    def __repr__(self):
        return f"Domínio: {self.domain}\nBase de Dados Diretoria: {self.data_file_path}\nBase de Dados: {self.cache}\n" \
               f"Servidor primário: {self.primary_server}\nServidores secundários: {self.secondary_servers}\n" \
               f"Domínios por defeito: {self.default_domains}\nTipo do servidor: {self.server_type}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log_file_path}"

    def zone_transfer_sp(self):
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket TCP
        socket_tcp.bind(("127.0.0.1", 24000))
        socket_tcp.listen()

        while True:
            connection, address = socket_tcp.accept()

            query_soaserial = connection.recv(1024).decode('utf-8')
            soaserial_response = self.interpret_query(query_soaserial) # Meter número da versão
            connection.sendall(soaserial_response.encode('utf-8')) # Enviar resposta à query com a versão

            query_init_transfer = connection.recv(1024).decode('utf-8') # Recebe query para pedir transferência
            init_transfer_response = self.interpret_query(query_init_transfer) # Verifica se os domínios são iguais
            connection.sendall(init_transfer_response.encode('utf-8'))  # Enviar resposta à query da transferência

            (message_id, flags, name, type_of_value) = parse_message(init_transfer_response)

            if "A" not in flags:
                connection.close()
                return # Não pode enviar a base de dados

            connection.sendall(file_to_string(self.data_file_path).encode('utf-8')) # Enviar base de dados

            connection.close()


    def zone_transfer_caller_ss(self):
        while True:
            self.zone_transfer_ss()

            soarefresh = self.cache.get_records_by_name_and_type(self.domain, "SOAREFRESH")[0].value

            sleep(int(soarefresh))


    def zone_transfer_ss(self):
        (ip_address, port) = self.parse_address(self.primary_server)

        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp.connect((ip_address, port))

        message = build_message(self.domain, "SOASERIAL", "Q+V") # Construir query para pedir versão da bd
        socket_tcp.sendall(message.encode('utf-8')) # Envia query

        message = socket_tcp.recv(1024).decode('utf-8') # Recebe query com a versão
        soaserial = self.cache.get_records_by_name_and_type(self.domain, "SOASERIAL")[0].value # Pega na versão

        (message_id, flags, value, type) = parse_message(message)

        if int(value) <= int(soaserial): #mesma versão logo a transferência de zona não se inicia
            #socket_tcp.close()
            return

        query = build_message(self.domain, "0", "Q+T") # Construir query para iniciar transferência de zona
        socket_tcp.sendall(query.encode('utf-8'))  # Envia query a pedir permissao
        response = socket_tcp.recv(1024).decode('utf-8')  # Recebe resposta com o numero de linhas

        (message_id, flags, name, type_of_value) = parse_message(response)

        if "A" not in flags:
            return

        # SS teve autorização para iniciar a transferencia de zone e vai receber a base de dados

        b = b'' # Iniciar  com 0 bytes
        while True:
            tmp = socket_tcp.recv(1024)

            if not tmp:
                break

            b += tmp

        #self.cache = parser_df(self.data_file_path) # MUDAR
        db = b.decode('utf-8')
        print(db)


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

