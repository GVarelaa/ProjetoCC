# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 30/10/22
# Data da última atualização: 11/11/22
# Descrição: Implementação de um servidor
# Última atualização: Documentação
import random
import socket
import threading
import time
from datetime import datetime

from dns_message import *
from resource_record import ResourceRecord


class Server:
    def __init__(self, config, log, port, timeout, handles_recursion):
        """
        Construtor de um objeto Server
        :param config: Estrutura com os dados de configuração
        :param log: Objetos Log
        :param port: Porta de atendimento
        """
        self.config = config
        self.log = log
        self.port = int(port)
        self.timeout = timeout
        self.handles_recursion = handles_recursion

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
            port = 5353  # porta default

        return ip_address, port

    def change_authority_flag(self, query):
        query.flags = ""
        for domain in self.config["DB"].keys():
            if domain == query.domain:
                query.flags = "A"
                break

    def is_resolution_server(self):
        return len(self.config["SS"].keys()) == 0 and len(self.config["SP"].keys()) == 0 and len(self.config["DB"].keys()) == 0

    def is_name_server(self):
        return len(self.config["SS"].keys()) != 0 or len(self.config["SP"].keys()) != 0

    def is_domain_in_dd(self, domain):
        return domain in self.config["DD"].keys()

    def has_default_domains(self):
        return len(self.config["DD"].keys()) != 0

    def find_next_step(self, query):
        server = None  # Top level domain server
        for record in query.authorities_values:
            if record.domain in query.domain:
                server = record.value

        if server is not None:
            for record in query.extra_values:
                if server == record.domain:
                    return Server.parse_address(record.value)

        if not self.is_name_server() and self.is_domain_in_dd(query.domain):
            return Server.parse_address(self.config["DD"][query.domain])

        return Server.parse_address(self.config["ST"][0])

    @staticmethod
    def find_next_domain(domain):
        ret = domain.split(".", 1)[1]
        if ret == "":
            ret = "."
        return ret

    def fill_extra_values(self, response_values, authorities_values):
        """
        Preenche os extra values relativos a uma query
        :param response_values: Lista com os response values
        :param authorities_values: Lista com os authorities values
        :return: Lista extra values preenchida
        """
        extra_values = list()

        for record in response_values:
            records = self.cache.get_records_by_domain_and_type(record.value, "A")
            extra_values += records

        for record in authorities_values:
            records = self.cache.get_records_by_domain_and_type(record.value, "A")
            extra_values += records

        return extra_values

    def cache_response(self, response):
        for record in response.response_values:
            self.cache.add_entry(record, response.domain)

        for record in response.authorities_values:
            self.cache.add_entry(record, response.domain)

        for record in response.extra_values:
            self.cache.add_entry(record, response.domain)

    def axfr_response(self, query):
        record = ResourceRecord(query.domain, query.type, str(self.cache.get_file_entries_by_domain(query.domain)[0]),0, -1,Origin.SP)
        query.flags = ""
        query.response_code = 0
        query.response_values.append(record)
        query.num_response = 1

        return query

    def build_response(self, query):
        """
        Formula a resposta a uma query
        :param query: Query a responder
        :return: Query já respondida
        """
        response_values = list()
        authorities_values = list()
        extra_values = list()

        found = False
        domain = query.domain

        while not found:
            response_values = self.cache.get_records_by_domain_and_type(domain, query.type)

            if len(response_values) == 0 and query.type == "A":  # Vai ver o seu CNAME
                cname = self.cache.get_records_by_domain_and_type(domain, "CNAME")
                if len(cname) > 0:
                    domain = cname[0].value
                    response_values = self.cache.get_records_by_domain_and_type(domain, query.type)

            authorities_values = self.cache.get_records_by_domain_and_type(domain, "NS")
            extra_values = self.fill_extra_values(response_values, authorities_values)

            if len(response_values) == 0 and len(authorities_values) == 0 and len(extra_values) == 0:
                domain = Server.find_next_domain(domain)

                if domain == ".": # Mudar
                    break
            else:
                found = True

        query.num_response = len(response_values)
        query.num_authorities = len(authorities_values)
        query.num_extra = len(extra_values)
        query.response_values = response_values
        query.authorities_values = authorities_values
        query.extra_values = extra_values

        if len(query.response_values) != 0:
            query.response_code = 0
            self.change_authority_flag(query)
        elif found:
            query.response_code = 1
            self.change_authority_flag(query)
        elif not found and "Q" not in query.flags:
            query.response_code = 2
            self.change_authority_flag(query)

        return query

    def receive_queries(self):
        """
        Recebe queries através de um socket udp e cria uma thread para cada query (thread-per-connection)
        """
        socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Criar socket UDP
        socket_udp.bind(("", self.port))

        while True:
            message, address = self.recvfrom_socket(socket_udp)
            threading.Thread(target=self.interpret_message, args=(message, address)).start()  # Thread per connection

        socket_udp.close()

    def sendto_socket(self, socket, message, address):
        socket.sendto(message.serialize(), address)

        if "Q" in message.flags:
            self.log.log_qe(message.domain, str(address), message.to_string())
        else:
            self.log.log_rp(message.domain, str(address), message.to_string())

    def recvfrom_socket(self, socket):
        try:
            message, address = socket.recvfrom(4096)
            message = DNSMessage.deserialize(message)

            if "Q" in message.flags:
                self.log.log_qr(message.domain, str(address), message.to_string())
            else:
                self.log.log_rr(message.domain, str(address), message.to_string())

            return message, address
        except socket.timeout as e:
            self.log.log_to("Foi detetado um timeout numa resposta a uma query.")


    def interpret_message(self, message, client):
        """
        Determina o próximo passo de uma mensagem DNS
        :param message: Mensagem DNS
        :param client: Endereço de onde foi enviada a mensagem
        :param socket_udp: Socket UDP
        """
        socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Criar socket UDP para enviar mensagens
        socket_udp.settimeout(self.timeout)

        if self.is_name_server():  # Se for SP ou SS para algum domínio
            if self.has_default_domains(): # Name server tem domínios por defeito
                if self.is_domain_in_dd(message.domain):  # Pode responder
                    response = self.build_response(message)  # Caso em que falha ao encontrar na cache

                    self.sendto_socket(socket_udp, response, client)
                else:  # Timeout?
                    self.log.log_to(message.domain, str(client), "Server has no permission to attend the query domain!")

            else:  # Pode responder a todos os domínios
                response = self.build_response(message)

                if "Q" in response.flags:  # Inicia o modo iterativo
                    next_step = self.find_next_step(response)
                    response_code = 1

                    while response_code == 1:
                        self.sendto_socket(socket_udp, response, next_step)

                        response, address = self.recvfrom_socket(socket_udp)

                        response_code = response.response_code
                        next_step = self.find_next_step(response)

                    if response_code == 0:
                        self.cache_response(response)

                    self.sendto_socket(socket_udp, response, client)
                else:
                    self.sendto_socket(socket_udp, response, client)

        elif self.is_resolution_server():  # Se for servidor de resolução
            response = self.build_response(message) # TODO: adicionar flag R se aceitar modo recursivo

            if response.response_code == 0 and "Q" not in response.flags:  # Foi à cache e encontrou resposta
                self.sendto_socket(socket_udp, response, client)
            else:
                # Inicia o processo iterativo
                # Primeiro vai aos DD
                # Senão vai so ST
                #if self.handles_recursion == False:
                    # Erro para o cliente
                next_step = self.find_next_step(response)

                response_code = 1
                while response_code == 1:
                    self.sendto_socket(socket_udp, response, next_step)

                    response, address = self.recvfrom_socket(socket_udp)

                    response_code = response.response_code
                    next_step = self.find_next_step(response)

                if response_code == 0:
                    self.cache_response(response)

                self.sendto_socket(socket_udp, response, client)
        else:
            response = self.build_response(message)

            self.sendto_socket(socket_udp, response, client)


    def sp_zone_transfer(self):
        """
            Cria o socket TCP e executa a transferência de zona para cada ligação estabelecida
        """
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp.bind(("127.0.0.1", self.port))
        socket_tcp.listen()

        while True:
            connection, address_from = socket_tcp.accept()

            threading.Thread(target=self.sp_zone_transfer_process, args=(connection, address_from)).start()

        socket_tcp.close()

    def sp_zone_transfer_process(self, connection, address_from):
        """
        Processo de transferência de zona
        :param connection: Conexão estabelecida
        :param address_from: Endereço do servidor secundário
        """
        while True:
            message = connection.recv(2048)  # Recebe queries (versão/pedido de transferência)

            if not message:
                break

            query = DNSMessage.deserialize(message)
            domain = query.domain

            if query.flags == "Q":  # Pedir versão/transferência de zona e envia
                self.log.log_qr(domain, str(address_from), query.to_string())

                if query.type == "AXFR":
                    self.log.log_zt(domain, str(address_from), "SP : Zone transfer started")
                    t_start = time.time()

                response = self.axfr_response(query)

                if response.response_code == 0:
                    self.log.log_rp(domain, str(address_from), response.to_string())
                    connection.sendall(response.serialize())

                else:
                    self.log.log_to(domain, str(address_from), "Query Miss")

            elif query.response_code == 0:  # Secundário aceitou linhas e respondeu com o nº de linhas
                self.log.log_rr(domain, str(address_from), query.to_string())

                num_entries, entries = self.cache.get_file_entries_by_domain(query.domain)
                lines_number = int(query.response_values[0].value)

                if lines_number == num_entries:
                    counter = 1
                    for record in entries:
                        if record.origin == Origin.FILE:
                            record = str(
                                counter) + " " + record.resource_record_to_string() + "\n"  # VER COM O LOST - INDICE
                            connection.sendall(record.encode('utf-8'))

                            counter += 1

                t_end = time.time()
                self.log.log_zt(domain, str(address_from), "SP : All entries sent", str(round(t_end - t_start, 5)) + "s")
                connection.close()
                break

    def ss_zone_transfer(self, domain):  # Ir aos seus SPs
        soaretry = 10  # soaretry default

        while True:
            success = self.ss_zone_transfer_process(domain)

            if not success:
                wait = soaretry
            else:
                self.cache.register_soaexpire(domain)
                soarefresh = int(self.cache.get_records_by_domain_and_type(domain, "SOAREFRESH")[0].value)
                soaretry = int(self.cache.get_records_by_domain_and_type(domain, "SOARETRY")[0].value)
                wait = soarefresh

            time.sleep(wait)

    def ss_zone_transfer_process(self, domain):
        """
        Processo de transferência de zona do servidor secundário
        """
        address, port = Server.parse_address(self.config["SP"][domain])

        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp.connect((address, port))

        expected_value = 1

        query = DNSMessage(random.randint(1, 65535), "Q", 0, domain, "SOASERIAL")
        socket_tcp.sendall(query.serialize())  # Envia query a pedir a versão da BD

        self.log.log_qe(domain, str(address), query.to_string())

        while True:
            message = socket_tcp.recv(2048)  # Recebe mensagens (queries/linhas da base de dados)
            message = DNSMessage.deserialize(message)

            if message.response_code == 0:
                if message.type == "SOASERIAL":
                    self.log.log_rr(domain, str(address), message.to_string())

                    ss_version = self.get_version(domain)
                    sp_version = message.response_values[0].value

                    if not self.interpret_version(sp_version, ss_version, socket_tcp, address, message, domain):
                        break

                    t_start = time.time()

                elif message.type == "AXFR":
                    self.log.log_rr(domain, str(address), message.to_string())

                    socket_tcp.sendall(message.serialize())  # Recebe o nº de linhas e reenvia
                    self.log.log_rp(domain, str(address), message.to_string())
                    break

        end = time.time() + 10
        success = False

        database_lines = ""
        while time.time() < end:
            message = socket_tcp.recv(2048)

            if not message:
                success = True
                break

            database_lines += message.decode('utf-8')

        if not success:
            return False

        database_lines = database_lines[:-1].split("\n")

        for line in database_lines:
            index, record = Server.remove_index(line)

            if index != expected_value:  # timeout
                self.log.log_ez(domain, str(address), "SS : Expected value does not match")

                socket_tcp.close()
                return False

            self.cache.add_entry(ResourceRecord.to_record(record, Origin.SP), domain)

            expected_value += 1

        t_end = time.time()
        self.log.log_zt(domain, str(address), "SS : Zone Transfer concluded successfully", str(round(t_end - t_start, 5)) + "s")
        socket_tcp.close()

        return True

    @staticmethod
    def remove_index(record):
        """
        Remove o índice de cada linha
        :param record: Linha
        :return: Índice, Linha sem o índice
        """
        fields = record.split(" ")
        index = int(fields[0])
        fields.remove(fields[0])

        record = " ".join(fields)

        return index, record

    def get_version(self, domain):
        """
        Obtém a versão da base de dados do servidor secundário
        :return: Versão
        """
        list = self.cache.get_records_by_domain_and_type(domain, "SOASERIAL")

        if len(list) == 0:
            ss_version = -1
        else:
            ss_version = list[0].value

        return ss_version

    def interpret_version(self, sp_version, ss_version, socket_tcp, address, response, domain):
        """
        Interpreta as versões do SP e do SS e envia a query a pedir transferência se a BD do SS estiver desatualizada
        :param sp_version: Versão do servidor primário
        :param ss_version: Versáo do servidor secundário
        :param socket_tcp: Socket TCP
        :param address: Endereço IP do servidor primário
        :param response: Resposta do servidor primário a interpretar
        :return: Bool
        """
        bool = False

        if float(sp_version) > float(ss_version):
            self.cache.free_sp_entries(domain)  # apagar as entradas "SP"

            query = DNSMessage(random.randint(1, 65535), "Q", 0, domain, "AXFR")  # Query AXFR

            socket_tcp.sendall(query.serialize())  # Envia query a pedir a transferência
            self.log.log_qe(domain, str(address), query.to_string())
            self.log.log_zt(domain, str(address), "SS : Zone Transfer started")

            bool = True

        else:  # BD está atualizada
            self.log.log_zt(domain, str(address), "SS : Database is up-to-date")
            socket_tcp.close()

        return bool
