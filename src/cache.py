# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 30/10/22
# Data da última atualização: 15/11/22
# Descrição: Implementação de sistema de cache de um servidor
# Última atualização: Implementação da funcionalidade SOAEXPIRE (hardcoded)

from resource_record import *
from datetime import datetime
import time

class Cache:
    def __init__(self, list=[]):
        """
        Construtor de um objeto Cache
        :param list: Lista vazia
        """
        record = ResourceRecord.create_free_record()
        list.append(record)
        self.list = list
        self.size = 0
        self.capacity = 1

    def __str__(self):
        """
        Devolve a representação em string de um objeto Cache
        """
        return str(self.list) + " " + str(self.size) + " " + str(self.capacity)

    def __repr__(self):
        """
        Devolve a representação oficial em string de um objeto Cache
        :return:
        """
        return str(self.list) + " " + str(self.size) + " " + str(self.capacity)

    def find_valid_entry(self, index, name, type):
        """
        Encontra a próxima entrada válida na cache(lista de records)
        :param index: Índice a partir do qual vai procurar
        :param name: Query domain name
        :param type: Query type
        :return: Índice da primeira entrada válida
        """
        i = 0
        found = False

        for record in self.list:
            if i > index and record.status == Status.VALID and record.name == name and record.type == type:
                found = True
                break

            if record.origin == Origin.OTHERS and datetime.timestamp(datetime.now()) - record.timestamp > record.ttl:
                record.status = Status.FREE

            i += 1

        if not found:
            return -1  # codigo de erro

        return i

    def add_entry(self, new_record):
        """
        Adiciona uma nova entrada na cache
        :param new_record: Nova entrada
        """
        if self.size == self.capacity:
            self.expand_cache()

        if new_record.origin == Origin.SP or new_record.origin == Origin.FILE:
            for i in range(self.capacity):
                if self.list[i].status == Status.FREE:
                    new_record.status = Status.VALID
                    new_record.timestamp = datetime.timestamp(datetime.now())
                    self.list[i] = new_record
                    break

        else:
            last_free = 0
            found = False
            for i in range(self.capacity):
                if self.list[i].status == Status.FREE:
                    last_free = i

                if self.list[i].name == new_record.name and self.list[i].type == new_record.type and \
                   self.list[i].value == new_record.value and self.list[i].priority == new_record.priority:
                    if self.list[i].origin == Origin.OTHERS:
                        self.list[i].timestamp = datetime.timestamp(datetime.now())
                        self.list[i].status = Status.VALID
                        found = True
                        break

            if not found:
                new_record.origin = Origin.OTHERS
                new_record.status = Status.VALID
                new_record.timestamp = datetime.timestamp(datetime.now())
                self.list[last_free] = new_record

        self.size += 1

    def get_valid_entries(self):
        """
        Obtém as entradas válidas da cache
        :return: Lista com as entradas válidas
        """
        entries = list()

        for record in self.list:
            if record.status == Status.VALID:
                entries.append(record)

            if record.origin == Origin.OTHERS and datetime.timestamp(datetime.now()) - record.timestamp > record.ttl:  #atualiza a cache
                record.status = Status.FREE

        return entries

    def get_num_valid_entries(self):
        """
        Obtém o número de entradas válidas
        :return: Número de entradas válidas
        """
        return len(self.get_valid_entries())

    def get_records_by_name_and_type(self, name, type):
        """
        Obtém a lista das entradas correspondentes com o name e o type.
        :param name: Domain name
        :param type: Type
        :return: Lista com as entradas que deram match
        """
        records = []
        index = 0

        while index < self.size:
            index = self.find_valid_entry(index, name, type)

            if index == -1:
                break

            record = self.list[index]
            records.append(record)

        return records

    def free_cache(self, domain):  #SOAEXPIRE
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
            if record.origin == Origin.OTHERS and datetime.timestamp(datetime.now()) - record.timestamp > record.ttl:  #atualiza a cache
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
