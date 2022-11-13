# Author: Gabriela Cunha, Guilherme Varela and Miguel Braga
# Created at: 11/11/22
# Last update date: 11/11/22
# Description: Module that implements the main server that receives and forwards dns messages to each of the servers
# Last update: Added documentation

import threading
from parse.configuration_parser import *
from dns import *
from log import *

def main():
    # Read command-line arguments
    args = sys.argv

    i = 1
    config_files = list() # List of config files of each server

    while not args[i].isnumeric():
        config_files.append(args[i])
        i = i+1

    port = args[i]
    timeout = args[i+1] # TTL
    mode = args[i+2] # Debug or not
    ip_address = ""

    if not validate_port(port):
        print("")# TODO Add log
        return

    lock = threading.Lock()

    # Parsing of all server files
    # TODO - change to dictionary
    servers = []
    for config_path in config_files:
        servers.append(parser_configuration(config_path, port, mode, lock))

    for server in servers:
        threading.Thread(target=server.run_server).start()


if __name__ == "__main__":
    main()

