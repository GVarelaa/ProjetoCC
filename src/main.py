import socket
import sys
import threading
from configuration_parser import *
import dns

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

    print(f"Estou à  escuta no {ip_address}:{port}")

    #threading.Thread(target=server.zone_transfer_sp).start()

    while True:
        message, address_from = socket_udp.recvfrom(1024)

        print(f"Recebi uma mensagem do cliente {address_from}")

        query = dns.string_to_dns(message.decode('utf-8'))
        #server.log.log_qr(address_from, message)

        if "Q" in query.flags:  # é query
            response = server.interpret_query(query) # objeto DNS

            if "A" in response.flags:
                socket_udp.sendto(response.dns_to_string().encode('utf-8'), address_from)  # enviar para o destinatário
            else:
                return  # MISS

        else:  # é uma resposta a uma query
            socket_udp.sendto(query.dns_to_string().encode('utf-8'), server.get_address(message))


    socket_udp.close()


if __name__ == "__main__":
    main()
