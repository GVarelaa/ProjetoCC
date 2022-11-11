import sys
import threading
from parse.configuration_parser import *
from queries.dns import *


def main():
    args = sys.argv
    config_path = args[1]
    port = args[2]
    timeout = args[3]
    mode = args[4]
    ip_address = '127.0.0.1'

    if not validate_port(port):
        return  # adicionar log

    server = parser_configuration(config_path)
    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket UDP
    socket_udp.bind((ip_address, int(port)))

    socket_tcp = s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"Estou à  escuta no {ip_address}:{port}")

    threading.Thread(target=server.zone_transfer(socket_tcp)).start()

    while True:
        message, address_from = socket_udp.recvfrom(1024)

        print(f"Recebi uma mensagem do cliente {address_from}")

        query = string_to_dns(message.decode('utf-8'))
        #server.log.log_qr(address_from, message)

        if "Q" in query.flags:  # é queries
            response = server.interpret_query(query) # objeto DNS

            if "A" in response.flags:
                socket_udp.sendto(response.query_to_string().encode('utf-8'), address_from) # enviar para o destinatário
            else:
                return  # MISS

        else:  # é uma resposta a uma queries
            socket_udp.sendto(query.query_to_string().encode('utf-8'), server.get_address(message))


    socket_udp.close()


if __name__ == "__main__":
    main()