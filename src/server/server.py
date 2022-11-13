# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 30/10/22
# Data da última atualização: 11/11/22
# Descrição: Implementação de um servidor
# Última atualização: Header
import socket
import threading
from dns import *
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

        self.soasp = None
        self.soaadmin = None
        self.soaserial = "-1"
        self.soarefresh = None
        self.soaretry = None
        self.soaexpire = None

        self.log.log_st("localhost", "1", "100", mode)



    def __str__(self):
        return f"Domínio: {self.domain}\nCache: {self.cache}\n" \
               f"Domínios por defeito: {self.default_domains}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log_path}"
    
    def __repr__(self):
        return f"Domínio: {self.domain}\nCache: {self.cache}\n" \
               f"Domínios por defeito: {self.default_domains}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log_path}"


    def parse_address(self, address):
        substrings = address.split(":")
        ip_address = substrings[0]

        if len(substrings) > 1:
            port = int(substrings[1])
        else:
            port = 5353 # porta default

        return (ip_address, port)

    def count_valid_lines(self):
        f = open(self.data_path, "r")
        counter = 0

        for line in f:
            if line[0] != "#" and len(line) > 1:
                counter += 1

        f.close()

        return counter

    def interpret_query(self, query):  # interpret_query
        response_values = list()
        authorities_values = list()
        extra_values = list()

        if query.flags == " " and query.type == "252":  # Query AXFR
            if self.domain == query.domain_name:
                record = ResourceRecord(query.domain_name, query.type, str(self.count_valid_lines()), -1, -1, "SP")

                query.flags = "A"
                query.response_values.append(record)
                query.number_of_values = 1

                return query
            else:
                return query
        else:
            response_values = self.cache.get_records_by_name_and_type(query.domain_name, query.type)

            if len(response_values) == 0 and query.type == "A": # Vai ver o seu CNAME
                cname = self.cache.get_records_by_name_and_type(query.domain_name, "CNAME")
                if len(cname) > 0:
                    cname = cname[0].value
                    response_values = self.cache.get_records_by_name_and_type(cname, query.type)

            if len(response_values) != 0:  # HIT
                authorities_values = self.cache.get_records_by_name_and_type(query.domain_name, "NS")
                extra_values = list()

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


    def run_server(self):
        socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Creation of the udp socket
        socket_udp.bind(("", int(self.port)))  # Binding to server ip

        self.log.log_ev("fasdfasd", "fasdfasd", "dafsd")

        threading.Thread(target=self.zone_transfer).start()  # New thread for the zone transfer

        while True:
            message, address_from = socket_udp.recvfrom(1024)  # Receives a message

            message = string_to_dns(message.decode('utf-8'))  # Decodes and converts to PDU

            if "Q" in message.flags:  # It is a query
                query = message

                self.log.log_qr(str(address_from), query.query_to_string())

                response = self.interpret_query(query)  # Create a response to that query

                if "A" in response.flags:  # Answer in cache/DB
                    self.log.log_rp(str(address_from), response.query_to_string())

                    socket_udp.sendto(response.query_to_string().encode('utf-8'), address_from)  # Send it back
                else:
                    self.log.log_to(str(address_from), "Query Miss")
                    return  # MISS

            else:  # It's a response to a query
                response = message

                self.log.log_rr(str(address_from), response.query_to_string())

                socket_udp.sendto(response.query_to_string().encode('utf-8'), self.get_address(message))

        socket_udp.close()



