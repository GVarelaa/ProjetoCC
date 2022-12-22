# Data de criação: 13/11/22
# Data da última atualização: 13/11/22
# Descrição: Receives queries for a given server
# Última atualização: Added comments
# TODO: Make it work for multiple servers
import socket
import threading
from parse.configuration_parser import *


def main():
    """
    Programa que corre um servidor
    """
    args = sys.argv
    config_path = args[1]  # Ficheiro de configuração
    port = args[2]  # Porta onde o servidor vai estar à escuta
    timeout = args[3]  # Tempo que o servidor vai esperar por uma resposta
    handles_recursion = args[4]

    print(port)

    if handles_recursion == 1:
        handles_recursion = True
    elif handles_recursion == 0:
        handles_recursion = False

    if len(args) > 5:
        mode = args[5]  # Modo (Debug/Shy)
    else:
        mode = "debug"

    try:
        server = parser_configuration(config_path, port, timeout, handles_recursion, mode)  # Parser dos dados
    except InvalidIPError:
        sys.stdout.write("Error running server configurations: Invalid IP address")
        return
    except InvalidPortError:
        sys.stdout.write("Error running server configurations: Invalid Port")
        return

    print(server.cache)
    print(server.log.file_paths)

    if len(server.config["SS"].values()) != 0: # Só recebe pedidos de transferência se for primário para algum domínio
        threading.Thread(target=server.sp_zone_transfer).start()

    for domain in server.config["SP"].keys(): # Vai pedir trransferência de zona para todos os seus servidor primários CUIDADO COM A CACHE (METER LOCKS)
        threading.Thread(target=server.ss_zone_transfer, args=(domain,)).start()

    threading.Thread(target=server.receive_queries).start()  # New thread for receiving messages from UDP


if __name__ == "__main__":
    main()
