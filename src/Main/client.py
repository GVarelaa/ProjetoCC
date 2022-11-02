# Author: Guilherme Varela
# Created at: 29/10/22
# Last update: 02/11/12
# Description: 

import socket
import sys
from src.QueryMessage.message import build_message

def main():
    args = sys.argv
    args.pop(0)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    args_split = args[0].split(":")
    ip_address = args_split[0]

    if len(args_split) > 1:
        port = args_split[1]
    else:
        port = 5353 # porta default

    name = args[1]
    type_of_value = args[2]
    flag = None
    if len(args) == 4:
        flag = args[3]

    message = build_message(name, type_of_value, flag)

    s.sendto(message.encode('utf-8'), (ip_address, port))


if __name__ == "__main__" :
    main()