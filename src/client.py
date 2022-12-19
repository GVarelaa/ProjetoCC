# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 13/11/22
# Descrição: Criação de query e envio para o servidor
# Última atualização: Added comments

import socket
import sys
import random
from dns_message import *


def main():
    """
    Programa responsável pelo envio de uma query para o servidor com os argumentos de input do cliente
    """
    args = sys.argv
    args.pop(0)

    args_split = args[0].split(":")

    message_id = random.randint(1, 65535)
    ip_address = args_split[0]
    port = 5353  # porta default
    domain_name = args[1]
    type = args[2]
    flags = "Q"
    debug = False

    if len(args_split) > 1:  # Se a porta for especificada, atualizar
        port = int(args_split[1])

    if 4 <= len(args) <= 5:
        if args[3] == "debug":
            debug = True

        elif args[3] == "R":
            flags = "Q+R"

            if args[4] == "debug":
                debug = True
            else:
                sys.stdout.write("Wrong mode")
                return

        else:
            sys.stdout.write("Wrong argument")
            return

    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Criar socket UDP

    query = DNSMessage(message_id, flags, 0, domain_name, type)  # Criar mensagem

    if debug:  # Enviar query para o socket do server
        socket_udp.sendto(query.to_string(), (ip_address, port))
    else:
        socket_udp.sendto(query.serialize(), (ip_address, port))

    message = socket_udp.recv(4096)  # Receber resposta do servidor

    if debug:  # Descodificação da resposta do servidor
        message = DNSMessage.from_string(message)
    else:
        message = DNSMessage.deserialize(message)

    sys.stdout.write(message.to_string())

    socket_udp.close()


if __name__ == "__main__":
    main()
