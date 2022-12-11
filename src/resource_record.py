# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 30/10/22
# Data da última atualização: 20/11/22
# Descrição: Representação de uma entrada no sistema de cache do servidor
# Última atualização: Documentação

from enum import Enum


class Origin(Enum):
    """
    Enumeração a representar a origem da entrada
    """
    FILE = 1
    SP = 2
    OTHERS = 3


class Status(Enum):
    """
    Enumeração a representar o status da entrada
    """
    FREE = 1
    VALID = 2


class ResourceRecord:
    def __init__(self, name, type, value, ttl, priority, origin):
        """
        Construtor de um objeto Resource Record
        :param name: Nome
        :param type: Tipo de valor
        :param value: Valor
        :param ttl: TTL
        :param priority: Prioridade
        :param origin: Origem
        """
        self.name = name
        self.type = type
        self.value = value
        self.ttl = ttl
        self.priority = priority
        self.origin = origin
        self.time_stamp = None
        self.status = None

    def __str__(self):
        """
        Devolve a representação em string do objeto Resource Record
        :return: String
        """
        return self.name + " " + self.type + " " + self.value + " " + str(self.ttl) + " " + str(self.priority) \
               + " " + str(self.origin) + " " + str(self.time_stamp) + " " + str(self.status)

    def __repr__(self):
        """
        Devolve a representação oficial em string do objeto Resource Record
        :return: String
        """
        return self.name + " " + self.type + " " + self.value + " " + str(self.ttl) + " " + str(self.priority) \
               + " " + str(self.origin) + " " + str(self.time_stamp) + " " + str(self.status)

    def resource_record_to_string(self):
        """
        Transforma um objeto Resource Record numa string
        :return: String
        """
        string = str(self.name) + " " + str(self.type) + " " + str(self.value) + " " + str(self.ttl) + " " + str(self.priority)
        return string

    @staticmethod
    def to_record(string, origin):
        """
        Transforma uma string num objeto Resource Record
        :param string: String
        :param origin: Origem
        :return: Record
        """
        fields = string.split(" ")
        priority = -1

        if len(fields) > 4:
            priority = fields[4]

        record = ResourceRecord(fields[0], fields[1], fields[2], int(fields[3]), priority, origin)

        return record

    @staticmethod
    def create_free_record():
        """
        Cria um objeto com o status FREE
        :return: Record
        """
        record = ResourceRecord("EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY")
        record.status = Status.FREE

        return record

    @staticmethod
    def encode_type(type):
        # Query Type
        # SOASP - 0, SOAADMIN - 1, SOASERIAL - 2, SOAREFRESH - 3, SOARETRY -4, SOAEXPIRE - 5, NS - 6, A - 7,
        # CNAME - 8, MX - 9, PTR - 10

        match type:
            case "SOASP":
                type = bin(0)
            case "SOAADMIN":
                type = bin(1)
            case "SOASERIAL":
                type = bin(2)
            case "SOAREFRESH":
                type = bin(3)
            case "SOARETRY":
                type = bin(4)
            case "SOAEXPIRE":
                type = bin(5)
            case "NS":
                type = bin(6)
            case "A":
                type = bin(7)
            case "CNAME":
                type = bin(8)
            case "MX":
                type = bin(9)
            case "PTR":
                type = bin(10)

        return type

    def serialize(self):
        bytes = b''
        bytes += len(self.name).to_bytes(1, "big", signed=False)
        bytes += self.name.encode('utf-8')
        bytes += ResourceRecord.encode_type(self.type)
        bytes += len(self.value).to_bytes(1, "big", signed=False)
        bytes += self.name.encode('utf-8')
        bytes += self.ttl.to_bytes(4, "big", signed=False)
        bytes += self.priority.to_bytes(1, "big", signed=False)

        return bytes

