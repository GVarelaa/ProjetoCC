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

    if len(args) > 4:
        mode = args[4]  # Modo (Debug/Shy)
    else:
        mode = "debug"

    server = parser_configuration(config_path, port, timeout, mode)  # Parser dos dados

    if server is None:
        return

    #threading.Thread(target=server.zone_transfer).start()    # New thread for the zone transfer
    threading.Thread(target=server.receive_queries).start()  # New thread for receiving messages from UDP


if __name__ == "__main__":
    main()
