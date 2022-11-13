# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de um servidor primário
# Última atualização: Header

import socket
import threading
from server import server
from queries.dns import *


class PrimaryServer(server.Server):
    def __init__(self, domain, default_domains, root_servers, log_path, mode, data_path, secondary_servers):
        super().__init__(domain, default_domains, root_servers, log_path, mode)
        self.data_path = data_path
        self.secondary_servers = secondary_servers

    def zone_transfer_process(self, connection, address):
        while True:
            message = connection.recv(1024).decode('utf-8') # Recebe queries (versão/pedido de transferência)

            if not message:
                break

            query = string_to_dns(message)

            if query.flags == "Q": # Pedir versão e envia
                response = self.interpret_query(query)
                connection.sendall(response.query_to_string().encode('utf-8'))
            elif query.flags == "": # Pedir transferência e envia número de linhas
                response = self.interpret_query(query)
                connection.sendall(response.query_to_string().encode('utf-8'))
            elif query.flags == "A" and query.type == "252": # Secundário aceitou linhas e respondeu com o nº de linhas
                lines_number = int(query.response_values[0].value)

                if lines_number == self.count_valid_lines():
                    file = open(self.data_path, "r")
                    i = 1
                    for line in file:
                        if len(line) > 1 and line[0] != '#':
                            line = str(i) + " " + line
                            connection.sendall(line.encode('utf-8'))

                            i += 1

                    file.close()
            else:
                return # CUIDADO

        connection.close()

    def zone_transfer(self):
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address = '127.0.0.1'
        port = 28004
        socket_tcp.bind((address, port))
        socket_tcp.listen()

        print(f"Estou à escuta no {address}:{port}")

        while True:
            connection, address = socket_tcp.accept()

            threading.Thread(target=self.zone_transfer_process, args=(connection, address)).start()

        socket_tcp.close()
