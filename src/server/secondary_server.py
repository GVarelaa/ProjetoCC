# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de um servidor secundário
# Última atualização: Header

import random
import socket
import time
from server import server
from queries.axfr import *
from parse.database_parser import *


class SecondaryServer(server.Server):
    def __init__(self, domain, default_domains, root_servers, log_path, mode, primary_server):
        super().__init__(domain, default_domains, root_servers, log_path, mode)
        self.primary_server = primary_server

    def __str__(self):
        return super().__str__() + \
               f"Server primário: {self.primary_server}\n"

    def __repr__(self):
        return super().__str__() + \
               f"Server primário: {self.primary_server}\n"

    def zone_transfer_process(self):
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        (address, port) = self.parse_address(self.primary_server)
        socket_tcp.connect((address, port))

        query = AXFR(random.randint(1, 65535), self.domain)

        socket_tcp.sendall(query.query_to_string().encode('utf-8')) # Envia query a pedir a transferência

        message = socket_tcp.recv(1024).decode('utf-8')  # Recebe a resposta da query

        response = string_to_axfr(message)  # Cria query AXFR

        if "A" not in response.flags:
            socket_tcp.close()  # (?)
            return

        lines_number_record = response.response_values[0]
        lines_number = int(lines_number_record.value)

        data = ""
        expected_value = 1
        while True:
            message = socket_tcp.recv(1024).decode('utf-8')

            if not message:
                break

            lines = message.split("\n")
            if "" in lines:
                lines.remove("")

            for line in lines:
                fields = line.split(" ")
                if int(fields[0]) != expected_value:
                    #timeout
                    socket_tcp.close()
                    return

                expected_value += 1

            data += message

            if lines_number == (expected_value-1):
                #timeout
                socket_tcp.close()
                break

        parser_database(self, data, "SP")
        print(self.cache)


    def zone_transfer(self):
        while True:
            self.zone_transfer_process()

            print(self.soarefresh)
            time.sleep(self.soarefresh)
