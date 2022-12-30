import socket
import sys
from dns_message import DNSMessage


class Client:
    def __init__(self, timeout, debug):
        self.timeout = timeout
        self.debug = debug
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Criar socket UDP

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

        except socket.timeout:
            raise
