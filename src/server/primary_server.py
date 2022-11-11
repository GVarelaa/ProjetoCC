# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de um servidor primário
# Última atualização: Header

import socket
from server import server
from queries.axfr import *


class PrimaryServer(server.Server):
    def __init__(self, domain, default_domains, data_path, root_servers, log_path, secondary_servers):
        super().__init__(domain, default_domains, root_servers, log_path)
        self.data_path = data_path
        self.secondary_servers = secondary_servers

    def zone_transfer(self, socket_tcp):
        address = '127.0.0.1'
        port = 26000
        socket_tcp.bind((address, port))
        socket_tcp.listen()

        print(f"Estou à escuta no {address}:{port}")

        while True:
            connection, address = socket_tcp.accept()

            message = connection.recv(1024).decode('utf-8')

            query = string_to_axfr(message) # Objeto AXFR

            if query.flags == "":
                response = self.interpret_query(query)
                connection.sendall(response.query_to_string().encode('utf-8'))
            else:
                return

            file = open(self.data_path, "r")
            i = 1
            for line in file:
                if len(line) > 1 and line[0] != '#':
                    line = str(i) + " " + line
                    connection.sendall(line.encode('utf-8'))

                    i+=1

            file.close()
            connection.close()



        socket_tcp.close()



