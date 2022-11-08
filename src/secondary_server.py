import server
from configuration_parser import *
from parser import *
from query_message.message import *

class SecondaryServer(server.Server):
    def __init__(self, domain, default_domains, data_path, root_servers, log_path, primary_server):
        super().__init__(domain, default_domains, data_path, root_servers, log_path)
        self.primary_server = primary_server

    def __str__(self):
        return super().__str__() + \
               f"Server primário: {self.primary_server}\n"

    def __repr__(self):
        return super().__str__() + \
               f"Server primário: {self.primary_server}\n"


    def zone_transfer_caller_ss(self):
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # socket TCP

        self.zone_transfer_initial(socket_tcp)

        """
        while True:
            soarefresh = self.cache.get_records_by_name_and_type(self.domain, "SOAREFRESH")[0].value

            sleep(int(soarefresh))

            self.zone_transfer_ss(socket_tcp)
        """



    def zone_transfer_initial(self, socket_tcp):
        (ip_address, port) = self.parse_address(self.primary_server)

        socket_tcp.connect((ip_address, port))

        query = build_message(self.domain, "0", "Q+T") # Construir query para iniciar transferência de zona
        socket_tcp.sendall(query.encode('utf-8'))  # Envia query a pedir permissao
        response = socket_tcp.recv(1024).decode('utf-8')  # Recebe resposta com o numero de linhas

        (message_id, flags, name, type) = parse_message(response)

        # FAZER INTERPRET RESPONSE

        if "A" not in flags:
            return

        b = b'' # Iniciar  com 0 bytes
        while True:
            tmp = socket_tcp.recv(1024)

            if not tmp:
                break

            b += tmp

        self.cache = parser_df(b.decode('utf-8')) # MUDAR
        print(self.cache)


    def zone_transfer_ss(self, socket_tcp):
        (ip_address, port) = self.parse_address(self.primary_server)

        socket_tcp.connect((ip_address, port))

        message = build_message(self.domain, "SOASERIAL", "Q+V") # Construir query para pedir versão da bd
        socket_tcp.sendall(message.encode('utf-8')) # Envia query

        message = socket_tcp.recv(1024).decode('utf-8') # Recebe query com a versão
        soaserial = self.cache.get_records_by_name_and_type(self.domain, "SOASERIAL")[0].value # Pega na versão

        (message_id, flags, value, type) = parse_message(message)

        if int(value) <= int(soaserial): #mesma versão logo a transferência de zona não se inicia
            #socket_tcp.close()
            return

        query = build_message(self.domain, "0", "Q+T") # Construir query para iniciar transferência de zona
        socket_tcp.sendall(query.encode('utf-8'))  # Envia query a pedir permissao
        response = socket_tcp.recv(1024).decode('utf-8')  # Recebe resposta com o numero de linhas

        (message_id, flags, name, type) = parse_message(response)

        if "A" not in flags:
            return

        # SS teve autorização para iniciar a transferencia de zone e vai receber a base de dados

        b = b'' # Iniciar  com 0 bytes
        while True:
            tmp = socket_tcp.recv(1024)

            if not tmp:
                break

            b += tmp

        #self.cache = parser_df(self.data_file_path) # MUDAR
        db = b.decode('utf-8')
        print(db)


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

    #socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket TCP


    print(f"Estou à  escuta no {ip_address}:{port}")

    threading.Thread(target=server.zone_transfer_caller_ss).start()

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
