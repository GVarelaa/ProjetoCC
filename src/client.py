# Author: Guilherme Varela
# Created at: 29/10/22
# Last update date: 02/11/12
# Description: Builds a dns query message and sends it to a server
# Last update: 

import socket
import sys
from dns import *
from query_message.message import build_message

def main():
    args = sys.argv
    args.pop(0)

    args_split = args[0].split(":")

    ip_address = args_split[0]
    port = 6000 # porta default
    domain_name = args[1]
    type = args[2]
    flags = "Q"

    if len(args_split) > 1:
        port = int(args_split[1])

    if len(args) == 4 and args[3] == "R":
        flags = "Q+R"

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    query = DNS(1, flags, domain_name, type)

    s.sendto(query.dns_to_string().encode('utf-8'), (ip_address, port))

    while True:
        msg, add = s.recvfrom(1024)
        msg = msg.decode('utf-8')

        print(msg)


if __name__ == "__main__" :
    main()