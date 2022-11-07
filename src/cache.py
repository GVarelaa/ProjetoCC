# Authors: Gabriela Cunha, Guilherme Varela and Miguel Braga
# Created at: 30/10/22
# Last update date: 4/11/22
# Description: Module that implements a database for storing data records (ex: A, NS, CNAME, etc)
# Last update: Changed data structure to dictionary of dictionaries and implemented the methods of put, get

from resource_record import ResourceRecord
from datetime import datetime

class Cache:
    def __init__(self, list=[]):
        record = ResourceRecord(None, None, None, None, None, None)
        record.status = "FREE"
        list.append(record)
        self.list = list

    def __str__(self):
        return str(self.list)

    def __repr__(self):
        return str(self.list)

    def find_entry(self, index, name, type):
        i = 1

        for record in self.list:
            if record.origin == "OTHERS" and datetime.timestamp(datetime.now()) - record.timestamp > record.ttl: #enums
                record.status = "FREE"

            if i-1 >= index:
                if record.status == "VALID" and record.name == name and record.type == type:
                    break

            i += 1

        return i

    def add_entry(self, new_record):
        if new_record.origin == "SP" or new_record.origin == "FILE":
            for i in range(len(self.list)):
                if self.list[i].status == "FREE":
                    new_record.index = i+1
                    new_record.status = "VALID"
                    new_record.timestamp = datetime.timestamp(datetime.now())
                    self.list[i] = new_record

        else:
            found = False
            last_free = 0

            for i in range(len(self.list)):
                if self.list[i].status == "FREE":
                    last_free = i

                if self.list[i].name == new_record.name and self.list[i].type == new_record.type and \
                   self.list[i].value == new_record.value and self.list[i].priority == new_record.priority:
                    if self.list[i].origin == "OTHERS":
                        self.list[i].timestamp = datetime.timestamp(datetime.now())
                        self.list[i].status = "VALID"
                        found = True

            if not found:
                self.list[last_free] = new_record

    def get_record_by_name_and_type(self, name, type):
        ind = self.find_entry(1, name, type)

        if ind > len(self.list):
            return None

        return ind

    # Gets all entries with the given name and type
    def get_records_by_name_and_type(self, name, type):
        records = []
        record_index = 1

        while record_index < len(self.list):
            record_index = self.find_entry(record_index, name, type)
            records.append(self.list[record_index-1]) #ta a adicionar o ultimo elemento mm que ele n de match CORRIGIR

        return records