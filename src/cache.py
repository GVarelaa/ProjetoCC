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
        record = create_free_record()
        list.append(record)
        self.list = list
        self.size = 0
        self.capacity = 1
        self.timestamp = time.localtime() # Time of the last SOAEXPIRE update
        self.soaexpire = 100 # Hardcoded for now

    def __str__(self):
        return str(self.list) + " " + str(self.size) + " " + str(self.capacity)

    def __repr__(self):
        return str(self.list) + " " + str(self.size) + " " + str(self.capacity)

    def find_valid_entry(self, index, name, type):
        i = 1
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
            for i in range(self.size):
                if self.list[i].status == "FREE":
                    new_record.index = i+1
                    new_record.status = "VALID"
                    new_record.timestamp = datetime.timestamp(datetime.now())
                    self.list[i] = new_record
                    break

        else:
            last_free = 0
            found = False
            for i in range(self.size):
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

    # Gets all entries with the given name and type
    def get_records_by_name_and_type(self, name, type):
        
        records = []
        record_index = 1

        while record_index < self.size + 1:
            record_index = self.find_valid_entry(record_index, name, type)

            if record_index == -1:
                break

            record = self.list[record_index-1]
            records.append(record)

        return records

    def test_soaexpire(self): # If SOAEXPIRE is valid, update all records relative to the domain that expired (???)
        if (time.mktime(time.localtime()) - time.mktime(self.timestamp) > self.soaexpire):
            self.free_cache("")
            self.timestamp = time.localtime()


    def free_cache(self, domain): #SOAEXPIRE
        for record in self.list:
            if record.name == domain:
                record.status = "FREE"


    def expand_cache(self):
        self.capacity = self.size * 2
        for i in range(self.capacity):
          if i >= self.size:
              self.list.append(create_free_record())

