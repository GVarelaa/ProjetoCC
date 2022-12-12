# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de queries
# Última atualização: Documentação
from bitstring import BitStream, BitArray
from resource_record import *
import re


class DNSMessage:
    def __init__(self, message_id, flags, response_code, domain_name, type, response=list(), authorities=list(), extra=list()):
        """
        Construtor de um objeto DNSMessage
        :param message_id: ID da mensagem
        :param flags: Flags
        :param domain_name: Nome do domínio
        :param type: Tipo
        """
        self.message_id = message_id
        self.flags = flags
        self.response_code = response_code
        self.number_of_values = len(response)
        self.number_of_authorities = len(authorities)
        self.number_of_extra_values = len(extra)
        self.domain_name = domain_name
        self.type = type
        self.response_values = response
        self.authorities_values = authorities
        self.extra_values = extra

    def __str__(self):
        """
        Devolve a representação em string do objeto DNSMessage
        :return: String
        """
        return str(self.message_id) + " " + str(self.flags) + " " + str(self.response_code) + " " \
               + str(self.number_of_values) + " " + str(self.number_of_authorities) + " " \
               + str(self.number_of_extra_values) + " " + str(self.domain_name) + " " + str(self.type) + "\n" \
               + str(self.response_values) + "\n" + str(self.authorities_values) + "\n" + str(self.extra_values)

    def __repr__(self):
        """
        Devolve a representação oficial em string do objeto DNSMessage
        :return: String
        """
        return str(self.message_id) + " " + str(self.flags) + " " + str(self.response_code) + " " \
               + str(self.number_of_values) + " " + str(self.number_of_authorities) + " "  \
               + str(self.number_of_extra_values) + " " + str(self.domain_name) + " " + str(self.type) + "\n" \
               + str(self.response_values) + "\n" + str(self.authorities_values) + "\n" + str(self.extra_values)

    def to_string(self):
        """
        Transforma um objeto DNSMessage numa string
        :return: String
        """
        string = str(self.message_id) + "," + str(self.flags) + "," + str(self.response_code) + "," \
                 + str(self.number_of_values) + "," + str(self.number_of_authorities) + "," \
                 + str(self.number_of_extra_values) + ";" + str(self.domain_name) + "," + str(self.type) + ";\n"

        for record in self.response_values:
            string += record.resource_record_to_string() + ",\n"

        string = string[:-2] + ";\n"

        for record in self.authorities_values:
            string += record.resource_record_to_string() + ",\n"

        string = string[:-2] + ";\n"

        for record in self.extra_values:
            string += record.resource_record_to_string() + ",\n"

        string = string[:-2] + ";"

        return string

    @staticmethod
    def is_query(message):  # Verificar função
        """
        Verifica se uma mensagem é uma query
        :param message: Mensagem
        :return: Bool
        """
        fields = message.split(";")

        if len(fields) < 2:
            return False

        fields.remove(fields[-1])

        header_fields = fields[0].split(",")
        data_fields = fields[1].split(",")

        if len(header_fields) < 6 or len(data_fields) < 2:
            return False

        return True

    def encode_flags(self):
        match self.flags:
            case "Q":
                flags = 0
            case "R":
                flags = 1
            case "A":
                flags = 2
            case "Q+R":
                flags = 3

        return BitArray(uint=flags, length=3) # MUDAMOS

    def serialize(self):
        bit_array = BitArray()

        # MessageID - 2 bytes
        msg_id = BitArray(uint=self.message_id, length=16)
        bit_array.append(msg_id)

        bit_array.append(self.encode_flags())

        response_code = BitArray(uint=self.response_code, length=2)
        bit_array.append(response_code)

        n_response = BitArray(uint=self.number_of_values, length=8)
        n_authorities = BitArray(uint=self.number_of_authorities, length=8)
        n_extra = BitArray(uint=self.number_of_extra_values, length=8)

        bit_array.append(n_response)
        bit_array.append(n_authorities)
        bit_array.append(n_extra)

        # Query Name
        len_domain = BitArray(uint=len(self.domain_name), length=8)
        domain = ResourceRecord.string_to_bit_array(self.domain_name)

        bit_array.append(len_domain)
        bit_array.append(domain)
        bit_array.append(ResourceRecord.encode_type(self.type))

        for record in self.response_values:
            bit_array.append(record.serialize())

        for record in self.authorities_values:
            bit_array.append(record.serialize())

        for record in self.extra_values:
            bit_array.append(record.serialize())

        bit_array.append(BitArray(uint=0, length=8 - len(bit_array) % 8)) # Completar multiplo de 8

        return bit_array.bytes

    @staticmethod
    def decode_flags_and_response_code(byte):
        byte = int.from_bytes(byte, "big", signed=False)
        bits = bin(byte)[2:]

        i = 0
        while i < 8 - len(bits):
            bits = "0" + bits

        flag = bits[:6]
        bits = bits[6:]
        r_code = bits

        flag = int(flag, 2)
        r_code = int(r_code, 2)

        match flag:
            case 0:
                flags = "Q"
            case 1:
                flags = "R"
            case 2:
                flags = "A"
            case 3:
                flags = "Q+R"

        return flags, r_code

    @staticmethod
    def deserialize(bytes):
        msg_id, bytes = ResourceRecord.take_bytes(bytes, 2)
        msg_id = int.from_bytes(msg_id, "big", signed=False)

        byte, bytes = ResourceRecord.take_bytes(bytes, 1)
        flags, r_code = DNSMessage.decode_flags_and_response_code(byte)

        num_response, bytes = ResourceRecord.take_bytes(bytes, 1)
        num_response = int.from_bytes(num_response, "big", signed=False)

        num_authorities, bytes = ResourceRecord.take_bytes(bytes, 1)
        num_authorities = int.from_bytes(num_authorities, "big", signed=False)

        num_extra, bytes = ResourceRecord.take_bytes(bytes, 1)
        num_extra = int.from_bytes(num_extra, "big", signed=False)

        len_domain_name, bytes = ResourceRecord.take_bytes(bytes, 1)
        len_domain_name = int.from_bytes(len_domain_name, "big", signed=False)
        domain, bytes = ResourceRecord.take_bytes(bytes, len_domain_name)
        domain = domain.decode('utf-8')

        type, bytes = ResourceRecord.take_bytes(bytes, 1)
        type = ResourceRecord.decode_type(type)

        response = list()
        authorities = list()
        extra = list()

        i = 0
        while i < num_response:
            record, bytes = ResourceRecord.deserialize(bytes)
            response.append(record)
            i += 1

        i = 0
        while i < num_authorities:
            record, bytes = ResourceRecord.deserialize(bytes)
            authorities.append(record)
            i += 1

        i = 0
        while i < num_extra:
            record, bytes = ResourceRecord.deserialize(bytes)
            extra.append(record)
            i += 1

        return DNSMessage(msg_id, flags, r_code, domain, type, response, authorities, extra)

