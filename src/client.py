# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 30/12/22
# Data da última atualização: 30/12/22
# Descrição: Implementação de um cliente
# Última atualização: Classe nova

import socket
import sys
from dns_message import DNSMessage


class Client:
    def __init__(self, timeout, debug):
        self.timeout = timeout
        self.debug = debug
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Criar socket UDP
        self.socket.settimeout(timeout)

    def __str__(self):
        return "Timeout: " + str(self.timeout) + "\nDebug: " + str(self.debug)

    def __repr__(self):
        return "Timeout: " + str(self.timeout) + "\nDebug: " + str(self.debug)

    def sendto_socket(self, message, address):
        if self.debug:  # Enviar query para o socket do server
            self.socket.sendto(message.to_string(), address)
        else:
            self.socket.sendto(message.serialize(), address)

    def recvfrom_socket(self):
        try:
            message = self.socket.recv(4096)  # Receber resposta do servidor

            if self.debug:  # Descodificação da resposta do servidor
                message = DNSMessage.from_string(message)
            else:
                message = DNSMessage.deserialize(message)

            sys.stdout.write(message.to_string())
            return message

        except socket.timeout:
            raise

    def parse_address(address):
        """
        Separa um endereço em endereço e porta
        :param address: Endereço IP
        :return: Endereço e porta
        """
        substrings = address.split(":")
        ip_address = substrings[0]

        if len(substrings) > 1:
            port = int(substrings[1])
        else:
            port = 5353  # porta default

        return ip_address, port

    @staticmethod
    def find_next_step(response, servers_visited=list()):
        """
        Encontra o próximo servidor a ser contactado
        :param query: Query recebida
        :return: Endereço do próximo servidor a ser contactado
        """
        for record1 in response.authorities_values:
            if record1.domain in response.domain:
                for record2 in response.extra_values:
                    address = Client.parse_address(record2.value)
                    if record1.value == record2.domain and address[0] not in servers_visited:
                        return address
