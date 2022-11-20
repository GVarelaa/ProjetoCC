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
        record = ResourceRecord.create_free_record()
        list.append(record)
        self.list = list
        self.size = 0
        self.capacity = 1

    def __str__(self):
        return str(self.list) + " " + str(self.size) + " " + str(self.capacity)

    def __repr__(self):
        return str(self.list) + " " + str(self.size) + " " + str(self.capacity)

    def find_valid_entry(self, index, name, type):
        i = 0
        found = False

        for record in self.list:
            if i > index and record.status == "VALID" and record.name == name and record.type == type:
                found = True
                break

            if record.origin == "OTHERS" and datetime.timestamp(datetime.now()) - record.timestamp > record.ttl: #enums
                record.status = "FREE"

            i += 1

        if not found:
            return -1 # codigo de erro

        return i

    def add_entry(self, new_record):
        if self.size == self.capacity:
            self.expand_cache()

        if new_record.origin == "SP" or new_record.origin == "FILE":
            for i in range(self.capacity):
                if self.list[i].status == "FREE":
                    new_record.status = "VALID"
                    new_record.timestamp = datetime.timestamp(datetime.now())
                    self.list[i] = new_record
                    break

        else:
            last_free = 0
            found = False
            for i in range(self.capacity):
                if self.list[i].status == "FREE":
                    last_free = i

                if self.list[i].name == new_record.name and self.list[i].type == new_record.type and \
                   self.list[i].value == new_record.value and self.list[i].priority == new_record.priority:
                    if self.list[i].origin == "OTHERS":
                        self.list[i].timestamp = datetime.timestamp(datetime.now())
                        self.list[i].status = "VALID"
                        found = True
                        break

            if not found:
                new_record.origin = "OTHERS"
                new_record.status = "VALID"
                new_record.timestamp = datetime.timestamp(datetime.now())
                self.list[last_free] = new_record

        self.size += 1

    def get_valid_entries(self):
        entries = list()

        for record in self.list:
            if record.status == "VALID":
                entries.append(record)

            if record.origin == "OTHERS" and datetime.timestamp(datetime.now()) - record.timestamp > record.ttl: #atualiza a cache
                record.status = "FREE"

        return entries

    def get_num_valid_entries(self):
        return len(self.get_valid_entries())

    # Gets all entries with the given name and type
    def get_records_by_name_and_type(self, name, type):
        records = []
        index = 0

        while index < self.size:
            index = self.find_valid_entry(index, name, type)

            if index == -1:
                break

            record = self.list[index]
            records.append(record)

        return records

    def free_cache(self, domain): #SOAEXPIRE
        for record in self.list:
            if record.name == domain:
                record.status = "FREE"

    def expand_cache(self):
        self.capacity = self.size * 2
        for i in range(self.capacity):
          if i >= self.size:
              self.list.append(ResourceRecord.create_free_record())

    def is_empty(self):
        len = 0
        for record in self.list:
            if record.origin == "OTHERS" and datetime.timestamp(datetime.now()) - record.timestamp > record.ttl: #atualiza a cache
                record.status = "FREE"

            if record.status == "VALID":
                len += 1

        return len == 0

    def free_sp_entries(self):
        for record in self.list:
            if record.origin == "SP":
                record.status = "FREE"
