# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 30/12/22
# Descrição: Executa um client
# Última atualização: Separação do parse do cliente em outro módulo

import socket
import sys
import random
from client import Client
from dns_message import *
from parse.client_parser import *


def main():
    """
    Programa responsável pelo envio de uma query para o servidor com os argumentos de input do cliente
    """
    try:
        address, domain, type, flags, timeout, debug = parser_client(sys.argv)

        client = Client(timeout, debug)

        query = DNSMessage(random.randint(1, 65535), flags, 0, domain, type)  # Criar mensagem
        client.sendto_socket(query, address)

        response_code = 1
        servers_visited = list()
        next_server = address[0]
        response = query
        while response_code == 1:
            try:
                response = client.recvfrom_socket()

            except socket.timeout:
                sys.stdout.write("Timeout occured")

                servers_visited.append(next_server[0])
                if next_server == Client.find_next_step(response, servers_visited):
                    break

            response_code = response.response_code
            next_server = Client.find_next_step(response, servers_visited)

        client.socket.close()

    except exceptions.InvalidArgument as e:
        sys.stdout.write(e.message)


if __name__ == "__main__":
    main()
