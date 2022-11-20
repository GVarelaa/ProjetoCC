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
    def __init__(self, domain, default_domains, root_servers, log, port, mode, data_path, secondary_servers):
        super().__init__(domain, default_domains, root_servers, log, port, mode)
        self.data_path = data_path
        self.secondary_servers = secondary_servers
    

    def zone_transfer_process(self, connection, address_from):
        while True:
            message = connection.recv(1024).decode('utf-8') # Recebe queries (versão/pedido de transferência)

            if not message:
                break

            query = string_to_dns(message)

            if query.flags == "Q": # Pedir versão/transferência de zona e envia
                self.log.log_qr(str(address_from), query.query_to_string())

                if query.type == "AXFR":
                    self.log.log_zt(str(address_from), "SP : Zone transfer started", "0")

                response = self.build_response(query)

                if "A" in response.flags:
                    self.log.log_rp(str(address_from), response.query_to_string())

                    connection.sendall(response.query_to_string().encode('utf-8'))

                else:
                    self.log.log_to(str(address_from), "Query Miss")

            elif query.flags == "A" and query.type == "AXFR": # Secundário aceitou linhas e respondeu com o nº de linhas
                self.log.log_rr(str(address_from), query.query_to_string())

                lines_number = int(query.response_values[0].value)

                if lines_number == self.cache.get_num_valid_entries():
                    entries = self.cache.get_valid_entries()

                    counter = 1
                    for record in entries:
                        if record.origin == "FILE":
                            record = str(counter) + " " + record.resource_record_to_string() + "\n"
                            connection.sendall(record.encode('utf-8'))

                            counter += 1

                self.log.log_zt(str(address_from), "SP : All entries sent", "0")

            else:
                self.log.log_ez(str(address_from), "SP : Unexpected message")

                connection.close()

                break # CUIDADO

        connection.close()

    def zone_transfer(self):
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp.bind(("", int(self.port)))  #TIRAR ISTO
        socket_tcp.listen()

        while True:
            connection, address_from = socket_tcp.accept()

            threading.Thread(target=self.zone_transfer_process, args=(connection, address_from)).start()

        socket_tcp.close()
