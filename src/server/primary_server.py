# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de um servidor primário
# Última atualização: Header

import socket
import threading
from server import server
from dns import *
import time


class PrimaryServer(server.Server):
    def __init__(self, domain, default_domains, root_servers, domain_log, all_log, port, mode, data_path, secondary_servers):
        super().__init__(domain, default_domains, root_servers, domain_log, all_log, port, mode)
        self.data_path = data_path
        self.secondary_servers = secondary_servers

    def zone_transfer_process(self, connection, address):
        self.domain_log.log_zt(str(address), "SP", "0")

        while True:
            message = connection.recv(1024).decode('utf-8') # Recebe queries (versão/pedido de transferência)

            if not message:
                break

            query = string_to_dns(message)

            if query.flags == "Q": # Pedir versão e envia
                response = self.build_response(query)
                connection.sendall(response.query_to_string().encode('utf-8'))

            elif query.flags == " ": # Pedir transferência e envia número de linhas
                response = self.build_response(query)
                connection.sendall(response.query_to_string().encode('utf-8'))

            elif query.flags == "A" and query.type == "252": # Secundário aceitou linhas e respondeu com o nº de linhas
                lines_number = int(query.response_values[0].value)

                if lines_number == self.cache.get_num_valid_entries():
                    entries = self.cache.get_valid_entries()

                    counter = 1
                    for record in entries:
                        if record.origin == "FILE":
                            record = str(counter) + " " + record.resource_record_to_string() + "\n"
                            connection.sendall(record.encode('utf-8'))

                            counter += 1

            else:
                self.domain_log.log_ez(str(address), "SP : Unexpected message")
                connection.close()
                return # CUIDADO

        self.domain_log.log_zt(str(address), "SP : Zone Transfer concluded successfully", "0")
        connection.close()

    def zone_transfer(self):
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp.bind(("", 28009)) #TIRAR ISOTO
        socket_tcp.listen()

        while True:
            connection, address = socket_tcp.accept()

            threading.Thread(target=self.zone_transfer_process, args=(connection, address)).start()

        socket_tcp.close()
