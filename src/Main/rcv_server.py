# Author: Miguel Braga
# Created at: 29/10/22
# Last update: 29/10/12
# Description: Implements a server
# Last update: Added main and basic structure

import sys
import socket
from server import PrimaryServer
from secondary_server import SecondaryServer

# Args: fileConfig1 fileConfig2 ... fileConfigN porta timeout debug
def main(): 
    args = sys.argv

    # Parameter processing
    for i in range(1, len(args)):
        # Parse file
        print(args[i])

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Teste

    servers = []
    servers.append(PrimaryServer())
    servers.append(SecondaryServer())

    for server in servers:
        server.interpretQuery([])

    # Teste

    #### Open socket

    # endereco = 
    # porta = 
    # s.bind((endereco, porta ))

    #### Receive datagrams indefinitely

    # while True:
        # msg, add = s.recvfrom(1024)
        #### Process query
        #### Identify relevant server
        #### PDU sent to server

    s.close()

if __name__ == "__main__":
    main()