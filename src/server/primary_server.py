import socket
from server import server
from queries.axfr import *


class PrimaryServer(server.Server):
    def __init__(self, domain, default_domains, data_path, root_servers, log_path, secondary_servers):
        super().__init__(domain, default_domains, root_servers, log_path)
        self.data_path = data_path
        self.secondary_servers = secondary_servers

    def zone_transfer(self, socket_tcp):
        address = '127.0.0.1'
        port = 5555
        socket_tcp.bind((address, port))
        socket_tcp.listen()

        print(f"Estou à escuta no {address}:{port}")

        while True:
            connection, address = socket_tcp.accept()

            message = connection.recv(1024).decode('utf-8')

            query = string_to_axfr(message) # Objeto AXFR

            if "" is query.flags:
                response = self.interpret_query(query)
                connection.sendall(response.query_to_string().encode('utf-8'))
            else:
                return

            file = open(self.data_path, "r")

            for line in file:

                connection.sendall(line.encode('utf-8'))

            file.close()
            connection.close()



        socket_tcp.close()



    def zone_transfer_sp(self):
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket TCP
        socket_tcp.bind(("127.0.0.1", 24000))
        socket_tcp.listen()

        while True:
            connection, address = socket_tcp.accept()

            """
            query_soaserial = connection.recv(1024).decode('utf-8')
            soaserial_response = self.interpret_query(query_soaserial) # Meter número da versão
            connection.sendall(soaserial_response.encode('utf-8')) # Enviar resposta à queries com a versão
            """

            query_init_transfer = connection.recv(1024).decode('utf-8') # Recebe queries para pedir transferência
            init_transfer_response = self.interpret_query(query_init_transfer) # Verifica se os domínios são iguais
            connection.sendall(init_transfer_response.encode('utf-8'))  # Enviar resposta à queries da transferência

            (message_id, flags, name, type_of_value) = parse_message(init_transfer_response)

            if "A" not in flags:
                connection.close()
                return # Não pode enviar a base de dados

            connection.sendall(file_to_string(self.data_file_path).encode('utf-8')) # Enviar base de dados

            connection.close()
