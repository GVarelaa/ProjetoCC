# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 30/10/22
# Data da última atualização: 11/11/22
# Descrição: Implementação de um servidor
# Última atualização: Header
import socket
import threading
import time

from dns_message import *
from resource_record import ResourceRecord

class Server:
    def __init__(self, domain, default_domains, root_servers, log, port, mode):
        self.mode = mode
        self.domain = domain
        self.default_domains = default_domains
        self.log = log
        self.root_servers = root_servers
        self.port = port

        self.cache = None

    def __str__(self):
        return f"Domínio: {self.domain}\nCache: {self.cache}\n" \
               f"Domínios por defeito: {self.default_domains}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log}"
    
    def __repr__(self):
        return f"Domínio: {self.domain}\nCache: {self.cache}\n" \
               f"Domínios por defeito: {self.default_domains}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log}"

    def parse_address(self, address):
        substrings = address.split(":")
        ip_address = substrings[0]

        if len(substrings) > 1:
            port = int(substrings[1])
        else:
            port = 5353 # porta default

        return (ip_address, port)

    def build_response(self, query):  # interpret_query
        response_values = list()
        authorities_values = list()
        extra_values = list()

        if query.type == "AXFR" and self.domain == query.domain_name:  # Query AXFR
            record = ResourceRecord(query.domain_name, query.type, str(self.cache.get_num_valid_entries()), -1, -1, Origin.SP)

            query.flags = "A"
            query.response_values.append(record)
            query.number_of_values = 1

            return query
        else:
            domain_name = query.domain_name # por causa do cname
            response_values = self.cache.get_records_by_name_and_type(domain_name, query.type)

            if len(response_values) == 0 and query.type == "A": # Vai ver o seu CNAME
                cname = self.cache.get_records_by_name_and_type(domain_name, "CNAME")
                if len(cname) > 0:
                    domain_name = cname[0].value
                    response_values = self.cache.get_records_by_name_and_type(domain_name, query.type)

            if len(response_values) != 0:  # HIT
                authorities_values = self.cache.get_records_by_name_and_type(domain_name, "NS")

                for record in response_values:
                    records = self.cache.get_records_by_name_and_type(record.value, "A")
                    extra_values += records

                for record in authorities_values:
                    records = self.cache.get_records_by_name_and_type(record.value, "A")
                    extra_values += records

                query.number_of_values = len(response_values)
                query.number_of_authorities = len(authorities_values)
                query.number_of_extra_values = len(extra_values)
                query.response_values = response_values
                query.authorities_values = authorities_values
                query.extra_values = extra_values

                if "R" in query.flags:
                    query.flags = "R+A"
                else:
                    query.flags = "A"

                return query

            else:  # MISS
                return query

    def receive_queries(self, port):
        socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creation of the udp socket
        socket_udp.bind(("", int(port)))  # Binding to server ip

        while True:
            message, address_from = socket_udp.recvfrom(1024)  # Receives a message

            threading.Thread(target=self.interpret_message, args=(message, address_from, socket_udp)).start()  # Thread per connection

        socket_udp.close()

    def interpret_message(self, message, address_from, socket_udp):
        message = DNSMessage.from_string(message.decode('utf-8'))  # Decodes and converts to PDU

        if "Q" in message.flags:  # It is a query
            query = message

            self.log.log_qr(str(address_from), query.to_string())

            response = self.build_response(query)  # Create a response to that query

            if "A" in response.flags:  # Answer in cache
                self.log.log_rp(str(address_from), response.to_string())

                socket_udp.sendto(response.to_string().encode('utf-8'), address_from)  # Send it back
            else:
                self.log.log_to(str(address_from), "Query Miss")

                # MISS e timeout

        else:  # It's a response to a query
            response = message

            self.log.log_rr(str(address_from), response.to_string())

            # Segunda fase



