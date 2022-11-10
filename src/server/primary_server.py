import socket
from server import server


class PrimaryServer(server.Server):
    def __init__(self, domain, default_domains, data_path, root_servers, log_path, secondary_servers):
        super().__init__(domain, default_domains, root_servers, log_path)
        self.data_path = data_path
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
