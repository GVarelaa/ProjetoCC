# Data de criação: 13/11/22
# Data da última atualização: 13/11/22
# Descrição: Receives queries for a given server
# Última atualização: Added comments
# TODO: Make it work for multiple servers
import socket
import threading
from parse.configuration_parser import *


def main():
    args = sys.argv
    config_path = args[1]       # Path of the config file of the server
    port = args[2]              # Port the server will be listening
    timeout = args[3]           # Time the server waits for a response

    if len(args) > 4:
        mode = args[4]              # Debug enabled or disabled
    else:
        mode = "debug"

    server = parser_configuration(config_path, port, timeout, mode)   # Parsing the config and database file, creating a server
    print(server.cache)
    if server is None:
        return

    threading.Thread(target=server.zone_transfer).start()    # New thread for the zone transfer
    threading.Thread(target=server.receive_queries, args=(port,)).start()  # New thread for receiving messages from UDP

if __name__ == "__main__":
    main()
