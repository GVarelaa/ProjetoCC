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
    def __init__(self, domain, default_domains, root_servers, log, port, mode):
        """
        Construtor de um objeto Server
        :param domain: Domínio
        :param default_domains: Lista de domínios por defeito
        :param root_servers: Lista de Root Servers
        :param log: Objeto Log
        :param port: Porta de atendimento
        :param mode: Modo de funcionamento (debug ou shy)
        """
        self.mode = mode
        self.domain = domain
        self.default_domains = default_domains
        self.log = log
        self.root_servers = root_servers
        self.port = int(port)

        self.cache = None

    def __str__(self):
        """
        Devolve a representação em string do objeto Server
        :return: String
        """
        return f"Domínio: {self.domain}\nCache: {self.cache}\n" \
               f"Domínios por defeito: {self.default_domains}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log}"
    
    def __repr__(self):
        """
        Devolve a representação oficial em string do objeto Server
        :return: String
        """
        return f"Domínio: {self.domain}\nCache: {self.cache}\n" \
               f"Domínios por defeito: {self.default_domains}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log}"

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
            domain_name = query.domain_name # por causa do cname

            response_values = self.cache.get_records_by_name_and_type(domain_name, query.type)

            if len(response_values) == 0 and query.type == "A": # Vai ver o seu CNAME
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
        socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creation of the udp socket
        socket_udp.bind(("", self.port))  # Binding to server ip

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
        message = DNSMessage.from_string(message.decode('utf-8'))  # Decodes and converts to PDU

        if "Q" in message.flags and "R" not in message.flags:  # It is a query
            query = message

            self.log.log_qr(str(address_from), query.to_string())

            response = self.build_response(query)  # Create a response to that query

            if "A" in response.flags:  # Answer in cache
                self.log.log_rp(str(address_from), response.to_string())

                socket_udp.sendto(response.to_string().encode('utf-8'), address_from)  # Send it back
            else:
                self.log.log_to(str(address_from), "Query Miss") # MISS e timeout

        else:  # It's a response to a query
            response = message

            self.log.log_rr(str(address_from), response.to_string())

            # Segunda fase



