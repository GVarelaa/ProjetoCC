# Author: Guilherme Varela
# Created at: 29/10/22
# Last update date: 02/11/12
# Description: Builds a dns query message and sends it to a server
# Last update: 

import socket
import sys
from query_message.message import build_message

def main():
    args = sys.argv
    args.pop(0)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    args_split = args[0].split(":")
    ip_address = args_split[0]

    if len(args_split) > 1:
        port = int(args_split[1])
    else:
        port = 6000 # porta default

    name = args[1]
    type_of_value = args[2]
    flag = "Q"
    if len(args) == 4 and args[3] == "R":
        flag = "Q+R"

    message = build_message(name, type_of_value, flag)

    s.sendto(message.encode('utf-8'), (ip_address, port))

    while True:
        msg, add = s.recvfrom(1024)
        msg = msg.decode('utf-8')

        print(msg)


if __name__ == "__main__" :
    main()