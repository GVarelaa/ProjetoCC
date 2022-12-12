# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 30/10/22
# Data da última atualização: 20/11/22
# Descrição: Representação de uma entrada no sistema de cache do servidor
# Última atualização: Documentação

from bitstring import BitStream, BitArray
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

        return BitArray(uint=type, length=4)

    @staticmethod
    def decode_type(type):
        match type:
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

    @staticmethod
    def string_to_bit_array(string):
        bit_array = BitArray()

        for char in string:
            ascii = ord(char)
            bit_array.append(BitArray(uint=ascii, length=8))

        return bit_array

    @staticmethod
    def bit_array_to_string(bit_stream, length):
        string = ""

        i = 0
        while i < length:
            int = bit_stream.read('uint:8')
            string += chr(int)

            i += 1

        return string

    def serialize(self):
        bit_array = BitArray()

        bit_array.append(BitArray(uint=len(self.name), length=8))
        bit_array.append(ResourceRecord.string_to_bit_array(self.name))

        bit_array.append(ResourceRecord.encode_type(self.type))

        bit_array.append(BitArray(uint=len(self.value), length=8))
        bit_array.append(ResourceRecord.string_to_bit_array(self.value))

        bit_array.append(BitArray(uint=self.ttl, length=32))

        if self.priority == -1:
            bit_array.append(BitArray(uint=0, length=1))
        else:
            bit_array.append(BitArray(uint=1, length=1))
            bit_array.append(BitArray(uint=self.priority, length=8))

        return bit_array

    @staticmethod
    def take_bytes(bytes, number):
        ret = bytes[:number]
        bytes = bytes[number:]

        return ret, bytes

    @staticmethod
    def deserialize(stream):
        len_name = stream.read('uint:8')
        name = ResourceRecord.bit_array_to_string(stream, len_name)

        type = ResourceRecord.decode_type(stream.read('uint:4'))

        len_value = stream.read('uint:8')
        value = ResourceRecord.bit_array_to_string(stream, len_value)

        ttl = stream.read('uint:32')

        has_priority = stream.read('uint:1')
        priority = -1

        if has_priority:
            priority = stream.read('uint:8')
        
        return ResourceRecord(name, type, value, ttl, priority)



