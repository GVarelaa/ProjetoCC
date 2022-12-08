# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 30/10/22
# Data da última atualização: 15/11/22
# Descrição: Implementação de sistema de cache de um servidor
# Última atualização: Implementação da funcionalidade SOAEXPIRE (hardcoded)
import threading

from resource_record import *
from datetime import datetime
import time


class Cache:
    def __init__(self, list=[]):
        """
        Construtor de um objeto Cache
        :param list: Lista vazia
        """
        self.domains = dict()
        self.lock = threading.Lock()

        # record = ResourceRecord.create_free_record()
        # list.append(record)
        # self.list = list

    def __str__(self):
        """
        Devolve a representação em string de um objeto Cache
        """
        return str(self.domains)

    def __repr__(self):
        """
        Devolve a representação oficial em string de um objeto Cache
        :return:
        """
        return str(self.domains)

    def add_entry(self, new_record, domain):
        """
        Adiciona uma nova entrada na cache
        :param new_record: Nova entrada
        """

        if domain not in self.domains.keys():
            list = list()
            record = ResourceRecord.create_free_record()
            list.append(record)

            self.domains[domain] = list

        list = self.domains[domain]
        found = False

        if new_record.origin == Origin.SP or new_record.origin == Origin.FILE:
            for i in range(len(list)):
                record = list[i]

                if record.origin == Origin.OTHERS and datetime.timestamp(datetime.now()) - record.timestamp > record.ttl:


                if record.status == Status.FREE:
                    new_record.status = Status.VALID
                    new_record.timestamp = datetime.timestamp(datetime.now())
                    list[i] = new_record
                    found = True
                    break

            if not found:
                new_record.status = Status.VALID
                new_record.timestamp = datetime.timestamp(datetime.now())
                self.domains[domain].append(new_record)


        else:
            last_free = 0
            for i in range(len(list)):
                record = list[i]

                if record.origin == Origin.OTHERS and datetime.timestamp(datetime.now()) - record.timestamp > record.ttl:
                    record.status = Status.FREE

                if record.status == Status.FREE:
                    last_free = i

                if record.name == new_record.name and record.type == new_record.type and record.value == new_record.value \
                    and record.priority == new_record.priority and record.ttl == new_record.ttl:

                    if record.origin == Origin.OTHERS:
                        record.timestamp = datetime.timestamp(datetime.now())
                        record.status = Status.VALID

                    found = True
                    break

                if not found:
                    new_record.status = Status.VALID
                    new_record.timestamp = datetime.timestamp(datetime.now())
                    self.domains[domain][last_free] = new_record

    def get_file_entries_by_domain(self, domain):
        """
        Obtém as entradas com origem ficheiro de um domínio da cache
        :return: Lista com as entradas de um domínio
        """
        entries = list()
        counter = 0

        for record in self.list:
            if record.origin == Origin.FILE and domain in record.name:
                entries.append(record)
                counter += 1

            if record.origin == Origin.OTHERS and datetime.timestamp(
                    datetime.now()) - record.timestamp > record.ttl:  # atualiza a cache
                record.status = Status.FREE

        return counter, entries

    def get_records_by_name_and_type(self, name, type, domain):
        """
        Obtém a lista das entradas correspondentes com o name e o type.
        :param name: Domain name
        :param type: Type
        :return: Lista com as entradas que deram match
        """
        list = self.domains[domain]
        records = []
        index = 0

        for i in range(len(list)):
            record = list[i]

            if record.origin == Origin.OTHERS and datetime.timestamp(datetime.now()) - record.timestamp > record.ttl:
                self.domains[domain][i]

            if record.name == name and record.type == type:
                records.append(record)

        return records

    def free_cache(self, domain):  # SOAEXPIRE
        """
        Liberta a cache, colocando as entradas a FREE
        :param domain: Nome do domínio
        """
        for record in self.list:
            if record.name == domain:
                record.status = Status.FREE

    def expand_cache(self):
        """
        Expande a cache para o dobro do tamanho
        """
        self.capacity = self.size * 2
        for i in range(self.capacity):
            if i >= self.size:
                self.list.append(ResourceRecord.create_free_record())

    def is_empty(self):
        """
        Verifica se a cache está vazia
        :return: Boolean
        """
        len = 0
        for record in self.list:
            if record.origin == Origin.OTHERS and datetime.timestamp(
                    datetime.now()) - record.timestamp > record.ttl:  # atualiza a cache
                record.status = Status.FREE

            if record.status == Status.VALID:
                len += 1

        return len == 0

    def free_sp_entries(self):
        """
        Liberta as entradas do servidor primário
        """
        for record in self.list:
            if record.origin == Origin.SP:
                record.status = Status.FREE
