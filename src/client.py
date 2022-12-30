# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 30/12/2022
# Descrição: Criação de query e envio para o servidor
# Última atualização: Separação do parse do cliente em outro módulo

import socket
import sys
import random
from dns_message import *
from parse.client_parser import *


def main():
    """
    Programa responsável pelo envio de uma query para o servidor com os argumentos de input do cliente
    """
    try:
        address, domain, type, flags, timeout, debug = parser_client(sys.argv)

    except exceptions.InvalidArgument as e:
        sys.stdout.write(e.message)

    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Criar socket UDP
    socket_udp.settimeout(timeout)

    query = DNSMessage(random.randint(1, 65535), flags, 0, domain, type)  # Criar mensagem

    if debug:  # Enviar query para o socket do server
        socket_udp.sendto(query.to_string(), (ip_address, port))
    else:
        socket_udp.sendto(query.serialize(), (ip_address, port))

    try:
        message = socket_udp.recv(4096)  # Receber resposta do servidor

        if debug:  # Descodificação da resposta do servidor
            message = DNSMessage.from_string(message)
        else:
            message = DNSMessage.deserialize(message)

        sys.stdout.write(message.to_string())

        socket_udp.close()

    except socket.timeout as e:
        sys.stdout.write("Timeout occured")
        socket_udp.close()


if __name__ == "__main__":
    main()


