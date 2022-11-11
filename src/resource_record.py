# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 30/10/22
# Data da última atualização: 11/11/22
# Descrição: Representação de uma entrada no sistema de cache do servidor
# Última atualização: Header

from enum import Enum


class Origin(Enum):
    FILE = 1
    SP = 2
    OTHERS = 3


class Status(Enum):
    FREE = 1
    VALID = 2


def create_free_record():
    record = ResourceRecord("vazio", "vazio", "vazio", "vazio", "vazio", "vazio")
    record.status = "FREE"

    return record


class ResourceRecord:
    def __init__(self, name, type, value, ttl, priority, origin):
        self.name = name
        self.type = type
        self.value = value
        self.ttl = ttl
        self.priority = priority
        self.origin = origin
        self.time_stamp = None
        self.index = None
        self.status = None

    def __str__(self):
        return self.name + " " + self.type + " " + self.value + " " + str (self.ttl) + " " + str(self.priority) \
               + " " + str(self.origin) + " " + str(self.time_stamp) + " " + str(self.index) + " " + str(self.status)

    def __repr__(self):
        return self.name + " " + self.type + " " + self.value + " " + str(self.ttl) + " " + str(self.priority) \
               + " " + str(self.origin) + " " + str(self.time_stamp) + " " + str(self.index) + " " + str(self.status)

    def resource_record_to_string(self):
        string = str(self.name) + " " + str(self.type) + " " + str(self.value) + " " + str(self.ttl) + " " + str(self.priority)
        return string
