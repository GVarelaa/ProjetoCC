# Author: Guilherme Varela
# Created at: 30/10/22
# Last update: 03/11/12
# Description: Implements a server, a Primary Server
# Last update: Added basic structure
import socket
import sys
import threading

from log import Log
from database_parser import *
from query_message.message import parse_message, build_query_response, build_query_db_version_response, \
    build_query_init_transfer_response


class Server:
    def __init__(self, domain, default_domains, data_path, root_servers, log_path):
        self.mode = None
        self.domain = domain
        self.default_domains = default_domains
        self.log_path = log_path
        self.log = Log(log_path) # Objeto do tipo log
        self.root_servers = root_servers
        self.cache = parser_database(data_path)

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


    def interpret_query(self, query): # interpret_query
        (message_id, flags, name, type) = parse_message(query)

        response_values = list()
        authorities_values = list()
        extra_values = list()

        if "T" in flags and self.domain == name: # Domínios são iguais (?)
            #entries = count_file_entries(self.data_file_path)
            #response = build_query_init_transfer_response(query, entries)

            return response

        elif "V" in flags:
            soaserial = self.cache.get_records_by_name_and_type(self.domain, "SOASERIAL")[0].value
            response = build_query_db_version_response(query, soaserial)

            return response

        elif "T" in flags:
            return query

        elif "R" in flags:
            return

        else:
            response_values = self.cache.get_records_by_name_and_type(name, type)

            if len(response_values) != 0:  # HIT
                authorities_values = self.cache.get_records_by_name_and_type(name, "NS")
                extra_values = list()

                for record in response_values:
                    records = self.cache.get_records_by_name_and_type(record.value, "A")
                    extra_values += records

                for record in authorities_values:
                    records = self.cache.get_records_by_name_and_type(record.value, "A")
                    extra_values += records

                response = build_query_response(query, response_values, authorities_values, extra_values)

                return response

            else:  # MISS
                return None



