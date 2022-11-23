# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de um servidor primário
# Última atualização: Documentação

import socket
import threading
from server.server import Server
from dns_message import *
import time


class PrimaryServer(Server):
    def __init__(self, domain, default_domains, root_servers, log, port, mode, data_path, secondary_servers):
        """
        Construtor de um objeto PrimaryServer
        :param domain: Nome do domínio
        :param default_domains: Lista de domínios por defeito
        :param root_servers: Lista de root servers
        :param log: Objeto Log
        :param port: Porta
        :param mode: Modo
        :param data_path: Ficheiro de dados
        :param secondary_servers: Lista dos endereços IP dos servidores secundários
        """
        super().__init__(domain, default_domains, root_servers, log, port, mode)
        self.data_path = data_path
        self.secondary_servers = secondary_servers

    def __str__(self):
        """
        Devolve a representação em string do objeto PrimaryServer
        :return: String
        """
        return super().__str__() + "Ficheiro de dados: " + self.data_path + "Servidores secundários: " \
               + str(self.secondary_servers) + "\n"

    def __repr__(self):
        """
        Devolve a representação oficial em string do objeto PrimaryServer
        :return: String
        """
        return super().__str__() + "Ficheiro de dados: " + self.data_path + "Servidores secundários: \ " \
                + str(self.secondary_servers) + "\n"

    def zone_transfer_process(self, connection, address_from):
        """
        Processo de transferência de zona
        :param connection: Conexão estabelecida
        :param address_from: Endereço do servidor secundário
        """
        while True:
            message = connection.recv(4096).decode('utf-8')  # Recebe queries (versão/pedido de transferência)

            if not message:
                break

            query = DNSMessage.from_string(message)

            if query.flags == "Q":  # Pedir versão/transferência de zona e envia
                self.log.log_qr(str(address_from), query.to_string())

                if query.type == "AXFR":
                    self.log.log_zt(str(address_from), "SP : Zone transfer started", "0")

                response = self.build_response(query)

                if "A" in response.flags:
                    self.log.log_rp(str(address_from), response.to_string())

                    connection.sendall(response.to_string().encode('utf-8'))

                else:
                    self.log.log_to(str(address_from), "Query Miss")

            elif query.flags == "A" and query.type == "AXFR":  # Secundário aceitou linhas e respondeu com o nº de linhas
                self.log.log_rr(str(address_from), query.to_string())

                lines_number = int(query.response_values[0].value)

                if lines_number == self.cache.get_num_valid_entries():
                    entries = self.cache.get_valid_entries()

                    counter = 1
                    for record in entries:
                        if record.origin == Origin.FILE:
                            record = str(counter) + " " + record.resource_record_to_string() + "\n"

                            connection.sendall(record.encode('utf-8'))

                            counter += 1

                self.log.log_zt(str(address_from), "SP : All entries sent", "0")

            else:
                self.log.log_ez(str(address_from), "SP : Unexpected message")
                break

        connection.close()

    def zone_transfer(self):
        """
        Cria o socket TCP e executa a transferência de zona para cada ligação estabelecida
        """
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp.bind(("", self.port))  #TIRAR ISTO int(self.port)
        socket_tcp.listen()

        while True:
            connection, address_from = socket_tcp.accept()

            threading.Thread(target=self.zone_transfer_process, args=(connection, address_from)).start()

        socket_tcp.close()
