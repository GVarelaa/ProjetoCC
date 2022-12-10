# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 30/10/22
# Data da última atualização: 11/11/22
# Descrição: Implementação de um servidor
# Última atualização: Documentação
import random
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
        domain = query.domain_name

        if query.type == "AXFR" and domain in self.config["SS"].keys():  # Query AXFR
            record = ResourceRecord(domain, query.type, str(self.cache.get_file_entries_by_domain(domain)[0]), -1, -1, Origin.SP)

            query.flags = "A"
            query.response_values.append(record)
            query.number_of_values = 1

        else:
            response_values = self.cache.get_records_by_name_and_type(domain, query.type)

            if len(response_values) == 0 and query.type == "A":  # Vai ver o seu CNAME
                cname = self.cache.get_records_by_name_and_type(domain, "CNAME")
                if len(cname) > 0:
                    domain = cname[0].value
                    response_values = self.cache.get_records_by_name_and_type(domain, query.type)

            authorities_values = self.cache.get_records_by_name_and_type(domain, "NS")
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

            if self.config["SP"].keys is not None or self.config["SS"].keys is not None: # Se o servidor for SP ou SS
                if domain in self.config["DD"].keys: # dominio estiver nos DDs
                    response = self.build_response(query)  # Constrói a resposta a essa query

                    if "A" in response.flags:  # Informação na cache
                        self.log.log_rp(domain, str(address_from), response.to_string())

                        socket_udp.sendto(response.to_string().encode('utf-8'), address_from)  # Envia a resposta
                    else:
                        self.log.log_to(domain, str(address_from), "Query Miss")  # MISS e timeout

                else: #timeout
                    self.log.log_to(domain, str(address_from), "Server has no permission to attend the query domain!")

            else: # Servidor resolução
                response = self.build_response(query)

                if "A" in response.flags:  # Informação na cache
                    self.log.log_rp(domain, str(address_from), response.to_string())

                    socket_udp.sendto(response.to_string().encode('utf-8'), address_from)  # Envia a resposta
                else: # Não tinha a resposta na cache e por isso vai aos DDs
                    if domain in self.config["DD"].keys: # Caso o dominio esteja nos DDs
                        dds = self.config["DD"][domain]

                        socket_udp.sendto(query.to_string().encode('utf-8'), dds[0])
                    else: # Dominio não está nos DDs e vai a um root server
                        root_servers = self.config["ST"]

                        socket_udp.sendto(query.to_string().encode('utf-8'), root_servers[0]) # Ver query a mandar

        else:  # É uma resposta a uma query
            response = message
            response.flags = "" # Tirar o A de autoritativo

            self.log.log_rr(domain, str(address_from), response.to_string())

            # Segunda fase

    def receive_zone_transfer(self):
        """
            Cria o socket TCP e executa a transferência de zona para cada ligação estabelecida
        """
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp.bind(("127.0.0.1", self.port))
        socket_tcp.listen()

        while True:
            connection, address_from = socket_tcp.accept()

            threading.Thread(target=self.receive_zone_transfer_process, args=(connection, address_from)).start()

        socket_tcp.close()

    def receive_zone_transfer_process(self, connection, address_from):
        """
        Processo de transferência de zona
        :param connection: Conexão estabelecida
        :param address_from: Endereço do servidor secundário
        """
        while True:
            message = connection.recv(4096).decode('utf-8')  # Recebe queries (versão/pedido de transferência)

            if not message:
                break

            query = DNSMessage.from_string(message)
            domain = query.domain_name

            if query.flags == "Q":  # Pedir versão/transferência de zona e envia
                self.log.log_qr(domain, str(address_from), query.to_string())

                if query.type == "AXFR":
                    self.log.log_zt(domain, str(address_from), "SP : Zone transfer started", "0")

                response = self.build_response(query)

                if "A" in response.flags:
                    self.log.log_rp(domain, str(address_from), response.to_string())

                    connection.sendall(response.to_string().encode('utf-8'))

                else:
                    self.log.log_to(domain, str(address_from), "Query Miss")

            elif query.flags == "A" and query.type == "AXFR":  # Secundário aceitou linhas e respondeu com o nº de linhas
                self.log.log_rr(domain, str(address_from), query.to_string())

                (num_entries, entries) = self.cache.get_file_entries_by_domain(query.domain_name)
                lines_number = int(query.response_values[0].value)
                print(num_entries)
                print(lines_number)

                if lines_number == num_entries:
                    counter = 1
                    for record in entries:
                        if record.origin == Origin.FILE:
                            record = str(counter) + " " + record.resource_record_to_string() + "\n"

                            connection.sendall(record.encode('utf-8'))

                            counter += 1

                self.log.log_zt(domain, str(address_from), "SP : All entries sent", "0")

            else:
                self.log.log_ez(domain, str(address_from), "SP : Unexpected message")
                break

        connection.close()


    def ask_for_zone_transfer(self, domain): # Ir aos seus SPs
        soarefresh = 10     # soarefresh default
        while True:
            self.ask_for_zone_transfer_process(domain)

            soarefresh = int(self.cache.get_records_by_name_and_type(domain, "SOAREFRESH")[0].value)
            time.sleep(soarefresh)

    def ask_for_zone_transfer_process(self, domain):
        """
        Processo de transferência de zona
        """
        (address, port) = Server.parse_address(self.config["SP"][domain])

        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_tcp.connect((address, port))

        expected_value = 1
        lines_number = 0

        query = DNSMessage(random.randint(1, 65535), "Q", domain, "SOASERIAL")
        socket_tcp.sendall(query.to_string().encode('utf-8'))  # Envia query a pedir a versão da BD

        self.log.log_qe(domain, str(address), query.to_string())

        while True:
            message = socket_tcp.recv(4096).decode('utf-8')  # Recebe mensagens (queries/linhas da base de dados)

            if not message:
                break

            if DNSMessage.is_query(message):
                response = DNSMessage.from_string(message)  # Cria query DNS

                if response.flags == "A" and response.type == "SOASERIAL":
                    self.log.log_rr(domain, str(address), response.to_string())

                    ss_version = self.get_version(domain)
                    sp_version = response.response_values[0].value

                    if not self.interpret_version(sp_version, ss_version, socket_tcp, address, response, domain):
                        break

                elif response.flags == "A" and response.type == "AXFR":
                    self.log.log_rr(domain, str(address), response.to_string())

                    lines_number = int(response.response_values[0].value)

                    socket_tcp.sendall(response.to_string().encode('utf-8'))  # Confirma o nº de linhas e reenvia

                    self.log.log_rp(domain, str(address), response.to_string())

            else:
                message = message[:-1]
                lines = message.split("\n")

                for line in lines:
                    (index, record) = Server.remove_index(line)

                    if index != expected_value:  # timeout
                        self.log.log_ez(domain, str(address), "SS : Expected value does not match")

                        socket_tcp.close()
                        break

                    self.cache.lock.acquire()
                    self.cache.add_entry(ResourceRecord.to_record(record, Origin.SP), domain)
                    self.cache.lock.release()

                    expected_value += 1

                if lines_number == (expected_value - 1):
                    self.log.log_zt(domain, str(address), "SS : Zone Transfer concluded successfully", "0")

                    socket_tcp.close()
                    break


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
        list = self.cache.get_records_by_name_and_type(domain, "SOASERIAL")

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

            query = DNSMessage(random.randint(1, 65535), "Q", domain, "AXFR")  # Query AXFR

            socket_tcp.sendall(query.to_string().encode('utf-8'))  # Envia query a pedir a transferência

            self.log.log_rp(domain, str(address), response.to_string())
            self.log.log_zt(domain, str(address), "SS : Zone Transfer started", "0")

            bool = True

        else:  # BD está atualizada
            self.log.log_zt(domain, str(address), "SS : Database is up-to-date", "0")

            socket_tcp.close()

        return bool
