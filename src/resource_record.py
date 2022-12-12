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
    def __init__(self, name, type, value, ttl, priority, origin=Origin.OTHERS):
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
                type = 0
            case "SOAADMIN":
                type = 1
            case "SOASERIAL":
                type = 2
            case "SOAREFRESH":
                type = 3
            case "SOARETRY":
                type = 4
            case "SOAEXPIRE":
                type = 5
            case "NS":
                type = 6
            case "A":
                type = 7
            case "CNAME":
                type = 8
            case "MX":
                type = 9
            case "PTR":
                type = 10

        return type.to_bytes(1, "big", signed=False)

    @staticmethod
    def decode_type(byte):
        # Query Type
        # SOASP - 0, SOAADMIN - 1, SOASERIAL - 2, SOAREFRESH - 3, SOARETRY -4, SOAEXPIRE - 5, NS - 6, A - 7,
        # CNAME - 8, MX - 9, PTR - 10
        byte = int.from_bytes(byte, "big", signed=False)

        match byte:
            case 0:
                type = "SOASP"
            case 1:
                type = "SOAADMIN"
            case 2:
                type = "SOASERIAL"
            case 3:
                type = "SOAREFRESH"
            case 4:
                type = "SOARETRY"
            case 5:
                type = "SOAEXPIRE"
            case 6:
                type = "NS"
            case 7:
                type = "A"
            case 8:
                type = "CNAME"
            case 9:
                type = "MX"
            case 10:
                type = "PTR"

        return type


    def serialize(self):
        bytes = b''
        bytes += len(self.name).to_bytes(1, "big", signed=False)
        bytes += self.name.encode('utf-8')
        bytes += ResourceRecord.encode_type(self.type)
        bytes += len(self.value).to_bytes(1, "big", signed=False)
        bytes += self.value.encode('utf-8')
        bytes += self.ttl.to_bytes(4, "big", signed=False)
        bytes += self.priority.to_bytes(1, "big", signed=False)

        return bytes

    @staticmethod
    def take_bytes(bytes, number):
        ret = bytes[:number]
        bytes = bytes[number:]

        return ret, bytes

    @staticmethod
    def deserialize(bytes):
        len_name, bytes = ResourceRecord.take_bytes(bytes, 1)
        len_name = int.from_bytes(len_name, "big", signed=False)

        name, bytes = ResourceRecord.take_bytes(bytes, len_name)
        name = name.decode('utf-8')

        type, bytes = ResourceRecord.take_bytes(bytes, 1)
        type = ResourceRecord.decode_type(type)

        len_value, bytes = ResourceRecord.take_bytes(bytes, 1)
        len_value = int.from_bytes(len_value, "big", signed=False)

        value, bytes = ResourceRecord.take_bytes(bytes, len_value)
        value = value.decode('utf-8')

        ttl, bytes = ResourceRecord.take_bytes(bytes, 4)
        ttl = int.from_bytes(ttl, "big", signed=False)

        priority, bytes = ResourceRecord.take_bytes(bytes, 1)
        priority = int.from_bytes(priority, "big", signed=False)
        
        return ResourceRecord(name, type, value, ttl, priority)



