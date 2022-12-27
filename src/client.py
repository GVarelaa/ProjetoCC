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
    flags = "Q"  # Flags default
    timeout = 10  # Valor de timeout default
    debug = True  # Modo debug ligado por default

    if len(args_split) > 1:  # Se a porta for especificada, atualizar
        port = int(args_split[1])

    if 4 <= len(args) <= 6:
        if args[3] == "R":
            flags = "Q+R"

            if len(args) > 4:
                if args[4].isdigit():
                    timeout = int(args[4])

                elif args[4] == "shy":
                    debug = False

                elif args[4] != "debug":
                    sys.stdout.write("Invalid timeout value or mode")
                    return

        elif args[3].isdigit():
            timeout = int(args[3])

            if len(args) > 4:
                if args[4] == "shy":
                    debug = False

                elif args[4] != "debug":
                    sys.stdout.write("Invalid mode")
                    return

        elif args[3] == "shy":
            debug = False

        elif args[4] != "debug":
            sys.stdout.write("Invalid flag, timeout value or mode")
            return

    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Criar socket UDP
    socket_udp.settimeout(timeout)

    query = DNSMessage(message_id, flags, 0, domain_name, type)  # Criar mensagem

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


