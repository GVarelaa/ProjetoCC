# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 30/10/22
# Data da última atualização: 11/11/22
# Descrição: Implementação de um servidor
# Última atualização: Documentação
import socket
import threading
import time

from dns_message import *
from resource_record import ResourceRecord


class Server:
    def __init__(self, config, log, port):
        """
        Construtor de um objeto Server
        :param config: Estrutura com os dados de configuração
        :param log: Objetos Log
        :param port: Porta de atendimento
        """
        self.config = config
        self.log = log
        self.port = int(port)

        self.cache = None

    def __str__(self):
        """
        Devolve a representação em string do objeto Server
        :return: String
        """
        return "fazer"
    
    def __repr__(self):
        """
        Devolve a representação oficial em string do objeto Server
        :return: String
        """
        return "fazer"

    @staticmethod
    def parse_address(address):
        """
        Separa um endereço em endereço e porta
        :param address: Endereço IP
        :return: Tuplo com o endereço e a porta
        """
        substrings = address.split(":")
        ip_address = substrings[0]

        if len(substrings) > 1:
            port = int(substrings[1])
        else:
            port = 5353 # porta default

        return (ip_address, port)

    def fill_extra_values(self, response_values, authorities_values):
        """
        Preenche os extra values relativos a uma query
        :param response_values: Lista com os response values
        :param authorities_values: Lista com os authorities values
        :return: Lista extra values preenchida
        """
        extra_values = list()

        for record in response_values:
            records = self.cache.get_records_by_name_and_type(record.value, "A")
            extra_values += records

        for record in authorities_values:
            records = self.cache.get_records_by_name_and_type(record.value, "A")
            extra_values += records

        return extra_values

    def build_response(self, query):
        """
        Formula a resposta a uma query
        :param query: Query a responder
        :return: Query já respondida
        """
        response_values = list()
        authorities_values = list()

        if query.type == "AXFR" and self.domain == query.domain_name:  # Query AXFR
            record = ResourceRecord(query.domain_name, query.type, str(self.cache.get_num_valid_entries()), -1, -1, Origin.SP)

            query.flags = "A"
            query.response_values.append(record)
            query.number_of_values = 1

        else:
            domain_name = query.domain_name

            response_values = self.cache.get_records_by_name_and_type(domain_name, query.type)

            if len(response_values) == 0 and query.type == "A":  # Vai ver o seu CNAME
                cname = self.cache.get_records_by_name_and_type(domain_name, "CNAME")
                if len(cname) > 0:
                    domain_name = cname[0].value
                    response_values = self.cache.get_records_by_name_and_type(domain_name, query.type)

            authorities_values = self.cache.get_records_by_name_and_type(domain_name, "NS")
            extra_values = self.fill_extra_values(response_values, authorities_values)

            if len(response_values) != 0:  # HIT
                query.number_of_values = len(response_values)
                query.number_of_authorities = len(authorities_values)
                query.number_of_extra_values = len(extra_values)
                query.response_values = response_values
                query.authorities_values = authorities_values
                query.extra_values = extra_values
                query.flags = "A"

        return query

    def receive_queries(self):
        """
        Recebe queries através de um socket udp e cria uma thread para cada query (thread-per-connection)
        """
        socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Criar socket UDP
        socket_udp.bind(("127.0.0.1", self.port))

        while True:
            message, address_from = socket_udp.recvfrom(4096)  # Receives a message

            threading.Thread(target=self.interpret_message, args=(message, address_from, socket_udp)).start()  # Thread per connection

        socket_udp.close()

    def interpret_message(self, message, address_from, socket_udp):
        """
        Determina o próximo passo de uma mensagem DNS
        :param message: Mensagem DNS
        :param address_from: Endereço de onde foi enviada a mensagem
        :param socket_udp: Socket UDP
        """
        message = DNSMessage.from_string(message.decode('utf-8'))  # Cria uma DNSMessage
        domain = message.domain_name

        if "Q" in message.flags and "R" not in message.flags:  # Verifica que é uma query
            query = message

            self.log.log_qr(domain, str(address_from), query.to_string())

            response = self.build_response(query)  # Constrói a resposta a essa query

            if "A" in response.flags:  # Informação na cache
                self.log.log_rp(domain, str(address_from), response.to_string())

                socket_udp.sendto(response.to_string().encode('utf-8'), address_from)  # Envia a resposta
            else:
                self.log.log_to(domain, str(address_from), "Query Miss")  # MISS e timeout

        else:  # É uma resposta a uma query
            response = message

            self.log.log_rr(domain, str(address_from), response.to_string())

            # Segunda fase

    def receive_zone_transfer(self):
        """
            Cria o socket TCP e executa a transferência de zona para cada ligação estabelecida
        """
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp.bind(("", self.port))
        socket_tcp.listen()

        while True:
            connection, address_from = socket_tcp.accept()

            threading.Thread(target=self.zone_transfer_process, args=(connection, address_from)).start()

        socket_tcp.close()

    def ask_for_zone_transfer(self): # Ir aos seus SPs
        while True:
            self.zone_transfer_process()
            # meter soarefresh default
            soarefresh = int(self.cache.get_records_by_name_and_type(self.domain, "SOAREFRESH")[0].value)
            time.sleep(soarefresh)