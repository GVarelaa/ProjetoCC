# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de um servidor secundário
# Última atualização: Header

import random
from server import server
from queries.axfr import *
from parse.database_parser import *


class SecondaryServer(server.Server):
    def __init__(self, domain, default_domains, root_servers, log_path, primary_server):
        super().__init__(domain, default_domains, root_servers, log_path)
        self.primary_server = primary_server

    def __str__(self):
        return super().__str__() + \
               f"Server primário: {self.primary_server}\n"

    def __repr__(self):
        return super().__str__() + \
               f"Server primário: {self.primary_server}\n"

    def zone_transfer(self, socket_tcp):
        (address, port) = self.parse_address(self.primary_server)
        socket_tcp.connect((address, port))

        query = AXFR(random.randint(1, 65535), self.domain)

        socket_tcp.sendall(query.query_to_string().encode('utf-8')) # Envia query a pedir a transferência

        message = socket_tcp.recv(1024).decode('utf-8')  # Recebe a resposta da query

        response = string_to_axfr(message)  # Cria query AXFR

        if "A" not in response.flags:
            socket_tcp.close()  # (?)
            return

        string = ""
        expected_value = 1
        while True:
            line = socket_tcp.recv(1024).decode('utf-8')

            if not line:
                break

            string += line

        parser_database(self, string, "SP")
        print(self.cache)