# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de um servidor secundário
# Última atualização: Header

import random
import socket
import time
import threading
from server.server import Server
from dns_message import *
import select



class SecondaryServer(Server):
    def __init__(self, domain, default_domains, root_servers, log, port, mode, primary_server):
        super().__init__(domain, default_domains, root_servers, log, port, mode)
        self.primary_server = primary_server
        self.thread_expire = False

    def __str__(self):
        return super().__str__() + f"Server primário: {self.primary_server}\n"

    def __repr__(self):
        return super().__str__() + f"Server primário: {self.primary_server}\n"

    def zone_transfer(self):
        while True:
            self.zone_transfer_process()   #Criar thread ?

            soarefresh = int(self.cache.get_records_by_name_and_type(self.domain, "SOAREFRESH")[0].value)

            time.sleep(soarefresh)

    def zone_transfer_process(self):
        (address, port) = Server.parse_address(self.primary_server)

        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp.connect((address, port))

        expected_value = 1
        lines_number = 0

        query = DNSMessage(random.randint(1, 65535), "Q", self.domain, "SOASERIAL")
        socket_tcp.sendall(query.to_string().encode('utf-8'))  # Envia query a pedir a versão da BD

        self.log.log_qe(str(address), query.to_string())

        while True:
            message = socket_tcp.recv(4096).decode('utf-8')  # Recebe mensagens (queries/linhas da base de dados)

            if not message:
                break

            if DNSMessage.is_query(message):
                response = DNSMessage.from_string(message)  # Cria query DNS

                if response.flags == "A" and response.type == "SOASERIAL":
                    self.log.log_rr(str(address), response.to_string())

                    ss_version = self.get_version()
                    sp_version = response.response_values[0].value

                    if not self.interpret_version(sp_version, ss_version, socket_tcp, address, response):
                        break

                elif response.flags == "A" and response.type == "AXFR":
                    self.log.log_rr(str(address), response.to_string())

                    lines_number = int(response.response_values[0].value)
                    #Confirma nº de linhas ?
                    socket_tcp.sendall(response.to_string().encode('utf-8'))  # Confirma o nº de linhas e reenvia

                    self.log.log_rp(str(address), response.to_string())

            else:
                message = message[:-1]
                lines = message.split("\n")

                for line in lines:
                    (index, record) = SecondaryServer.remove_index(line)

                    if index != expected_value:  # timeout
                        self.log.log_ez(str(address), "SS : Expected value does not match")

                        socket_tcp.close()
                        break

                    self.cache.add_entry(ResourceRecord.to_record(record, Origin.SP))

                    expected_value += 1

                if lines_number == (expected_value-1):
                    self.log.log_zt(str(address), "SS : Zone Transfer concluded successfully", "0")

                    socket_tcp.close()
                    break
                #else: quando o tempo predefinido se esgotar, o SS termina a conexão. Deve tentar após SOARETRY segundos

    @staticmethod
    def remove_index(record):
        fields = record.split(" ")
        index = int(fields[0])
        fields.remove(fields[0])

        record = " ".join(fields)

        return (index, record)
    def get_version(self):
        list = self.cache.get_records_by_name_and_type(self.domain, "SOASERIAL")

        if len(list) == 0:
            ss_version = -1
        else:
            ss_version = list[0].value

        return ss_version
    def interpret_version(self, sp_version, ss_version, socket_tcp, address, response):
        bool = False

        if float(sp_version) > float(ss_version):
            self.cache.free_sp_entries()  # apagar as entradas "SP"

            query = DNSMessage(random.randint(1, 65535), "Q", self.domain, "AXFR")  # Query AXFR

            socket_tcp.sendall(query.to_string().encode('utf-8'))  # Envia query a pedir a transferência

            self.log.log_rp(str(address), response.to_string())

            self.log.log_zt(str(address), "SS : Zone Transfer started", "0")

            bool = True

        else:  # BD está atualizada
            self.log.log_zt(str(address), "SS : Database is up-to-date", "0")

            socket_tcp.close()

        return bool
