# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de um servidor secundário
# Última atualização: Header

import random
import socket
import time
import threading
from server import server
from dns import *
import select


class SecondaryServer(server.Server):
    def __init__(self, domain, default_domains, root_servers, domain_log, all_log, port, mode, primary_server):
        super().__init__(domain, default_domains, root_servers, domain_log, all_log, port, mode)
        self.primary_server = primary_server
        self.thread_expire = False

    def __str__(self):
        return super().__str__() + \
               f"Server primário: {self.primary_server}\n"

    def __repr__(self):
        return super().__str__() + \
               f"Server primário: {self.primary_server}\n"

    def zone_transfer(self):
        while True:
            self.zone_transfer_process()   #Criar thread ?

            soarefresh = int(self.cache.get_records_by_name_and_type(self.domain, "SOAREFRESH")[0].value)

            time.sleep(soarefresh)

    def zone_transfer_process(self):
        (address, port) = self.parse_address(self.primary_server)

        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp.connect((address, port))

        expected_value = 1
        lines_number = 0

        query = DNS(random.randint(1, 65535), "Q", self.domain, "SOASERIAL")
        socket_tcp.sendall(query.query_to_string().encode('utf-8'))  # Envia query a pedir a versão da BD

        self.domain_log.log_qe(str(address), query.query_to_string())
        self.all_log.log_qe(str(address), query.query_to_string())

        while True:
            message = socket_tcp.recv(1024).decode('utf-8')  # Recebe mensagens (queries/linhas da base de dados)

            if not message:
                break

            if is_query(message):
                response = string_to_dns(message)  # Cria query DNS

                if response.flags == "A" and response.type == "SOASERIAL":
                    self.domain_log.log_rr(str(address), response.query_to_string())
                    self.all_log.log_rr(str(address), response.query_to_string())

                    list = self.cache.get_records_by_name_and_type(self.domain, "SOASERIAL")

                    if len(list) == 0:
                        ss_version = -1
                    else:
                        ss_version = list[0].value

                    sp_version = response.response_values[0].value

                    if float(sp_version) > float(ss_version):
                        self.cache.free_sp_entries()                                    # apagar as entradas "SP"

                        query = DNS(random.randint(1, 65535), "Q", self.domain, "AXFR")  # Query AXFR

                        socket_tcp.sendall(query.query_to_string().encode('utf-8'))  # Envia query a pedir a transferência

                        self.domain_log.log_rp(str(address), response.query_to_string())
                        self.all_log.log_rp(str(address), response.query_to_string())

                        self.domain_log.log_zt(str(address), "SS : Zone Transfer started", "0")
                        self.all_log.log_zt(str(address), "SS : Zone Transfer started", "0")

                    else: # BD está atualizada
                        self.domain_log.log_zt(str(address), "SS : Database is up-to-date", "0")
                        self.all_log.log_zt(str(address), "SS : Database is up-to-date", "0")

                        socket_tcp.close()
                        break

                elif response.flags == "A" and response.type == "AXFR":
                    self.domain_log.log_rr(str(address), response.query_to_string())
                    self.all_log.log_rr(str(address), response.query_to_string())

                    lines_number = int(response.response_values[0].value)
                    #Confirma nº de linhas ?
                    socket_tcp.sendall(response.query_to_string().encode('utf-8'))  # Confirma o nº de linhas e reenvia

                    self.domain_log.log_rp(str(address), response.query_to_string())
                    self.all_log.log_rp(str(address), response.query_to_string())

            else:
                lines = message.split("\n")
                if "" in lines:
                    lines.remove("")

                for line in lines:
                    fields = line.split(" ")

                    if int(fields[0]) != expected_value: # timeout
                        self.domain_log.log_ez(str(address), "SS : Expected value does not match")
                        self.all_log.log_ez(str(address), "SS : Expected value does not match")

                        socket_tcp.close()
                        return

                    fields.remove(fields[0])

                    record = " ".join(fields)
                    record = string_to_record(record)

                    self.cache.add_entry(record)

                    expected_value += 1

                if lines_number == (expected_value-1):
                    self.domain_log.log_zt(str(address), "SS : Zone Transfer concluded successfully", "0")
                    self.all_log.log_zt(str(address), "SS : Zone Transfer concluded successfully", "0")

                    socket_tcp.close()
                    break
                #else: quando o tempo predefinido se esgotar, o SS termina a conexão. Deve tentar após SOARETRY segundos