import sys
import threading
import server
import socket
from src.parser import *
from src.query_message.message import *

class PrimaryServer(server.Server):
    def __init__(self, config_file_path, mode):
        (domain, data_file_path, primary_server,
         secondary_servers, default_domains,
         root_servers_file_path, log_file_path) = parser_cf(config_file_path)

        super().__init__(domain, data_file_path, default_domains, root_servers_file_path, log_file_path, mode)
        self.data_file_path = data_file_path
        self.secondary_servers = secondary_servers


    def zone_transfer_sp(self):
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket TCP
        socket_tcp.bind(("127.0.0.1", 24000))
        socket_tcp.listen()

        while True:
            connection, address = socket_tcp.accept()

            """
            query_soaserial = connection.recv(1024).decode('utf-8')
            soaserial_response = self.interpret_query(query_soaserial) # Meter número da versão
            connection.sendall(soaserial_response.encode('utf-8')) # Enviar resposta à query com a versão
            """

            query_init_transfer = connection.recv(1024).decode('utf-8') # Recebe query para pedir transferência
            init_transfer_response = self.interpret_query(query_init_transfer) # Verifica se os domínios são iguais
            connection.sendall(init_transfer_response.encode('utf-8'))  # Enviar resposta à query da transferência

            (message_id, flags, name, type_of_value) = parse_message(init_transfer_response)

            if "A" not in flags:
                connection.close()
                return # Não pode enviar a base de dados

            connection.sendall(file_to_string(self.data_file_path).encode('utf-8')) # Enviar base de dados

            connection.close()



def main():
    args = sys.argv
    config_filepath = args[1]
    port = args[2]
    timeout = args[3]
    mode = args[4]
    ip_address = '127.0.0.1'

    if not validate_port(port):
        return  # adicionar log

    server = PrimaryServer(config_filepath, mode)

    socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket UDP
    socket_udp.bind((ip_address, int(port)))

    print(f"Estou à  escuta no {ip_address}:{port}")


    threading.Thread(target=server.zone_transfer_sp).start()


    while True:
        message, address_from = socket_udp.recvfrom(1024)
        message = message.decode('utf-8')

        print(f"Recebi uma mensagem do cliente {address_from}")

        is_query = server.is_query(message)

        server.log.log_qr(address_from, message)

        server.add_address(message, address_from)

        if is_query:  # é query
            response = server.interpret_query(message)

            if response:
                socket_udp.sendto(response.encode('utf-8'), address_from)  # enviar para o destinatário
            else:
                return  # MISS

        else:  # é uma resposta a uma query
            socket_udp.sendto(message.encode('utf-8'), server.get_address(message))

    socket_udp.close()


if __name__ == "__main__":
    main()


