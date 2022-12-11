# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de queries
# Última atualização: Documentação

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
    def from_string(query):
        """
        Transforma uma string num objeto DNSMessage
        :param query: Mensagem (string)
        :return: Objeto DNSMessage
        """
        (message_id, flags, response_code, num_response_values, num_authorities_values,
         num_extra_values, name, type, response_values, authorities_values, extra_values) = parse_message(query)

        query = DNSMessage(message_id, flags, name, type)
        query.response_code = int(response_code)
        query.number_of_values = int(num_response_values)
        query.number_of_authorities = int(num_authorities_values)
        query.number_of_extra_values = int(num_extra_values)

        for value in response_values:
            fields = value.split(" ")
            priority = -1

            if len(fields) > 4:
                priority = fields[4]

            record = ResourceRecord(fields[0], fields[1], fields[2], int(fields[3]), priority, "")
            query.response_values.append(record)

        for value in authorities_values:
            fields = value.split(" ")
            priority = -1

            if len(fields) > 4:
                priority = fields[4]

            record = ResourceRecord(fields[0], fields[1], fields[2], int(fields[3]), priority, "")
            query.authorities_values.append(record)

        for value in extra_values:
            fields = value.split(" ")
            priority = -1

            if len(fields) > 4:
                priority = fields[4]

            record = ResourceRecord(fields[0], fields[1], fields[2], int(fields[3]), priority, "")
            query.extra_values.append(record)

        return query

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

    def serialize(self):
        bytes = b''

        # MessageID - 2 bytes
        m_id = self.message_id.to_bytes(2, "big", signed=False)
        bytes += m_id

        # Flags - 6 bits
        # Q - 0, R - 1, A - 2 e Q+R - 3
        match self.flags:
            case "Q":
                flags = bin(0)
            case "R":
                flags = bin(1)
            case "A":
                flags = bin(2)
            case "Q+R":
                flags = bin(3)

        # Response Code - 2 bits
        # 0 - 0, 1 - 1, 2 - 2 e 3 - 3
        r_code = bin(self.response_code)
        snd_byte = r_code + flags[2:]

        bytes += r_code + snd_byte

        n_values = self.number_of_values.to_bytes(1, "big", signed=False)
        n_authorities = self.number_of_authorities.to_bytes(1, "big", signed=False)
        n_extra = self.number_of_extra_values.to_bytes(1, "big", signed=False)

        bytes += n_values + n_authorities + n_extra

        # Query Name
        len_domain = len(self.domain_name).to_bytes(1, "big", signed=False)
        domain = self.domain_name.encode('utf-8')

        bytes += len_domain + domain

        # Query Type
        # SOASP - 0, SOAADMIN - 1, SOASERIAL - 2, SOAREFRESH - 3, SOARETRY -4, SOAEXPIRE - 5, NS - 6, A - 7,
        # CNAME - 8, MX - 9, PTR - 10
        type = ResourceRecord.encode_type(self.type)

        bytes += type

        for record in self.response_values:
            bytes += record.serialize()

        for record in self.authorities_values:
            bytes += record.serialize()

        for record in self.extra_values:
            bytes += record.serialize()

        return bytes

    @staticmethod
    def deserialize(byte_array):
        m_id = ""
        flags = ""
        response_code = ""
        domain = ""
        type = ""
        response = list()
        authorities = list()
        extra = list()

        return DNSMessage(m_id, flags, response_code, domain, type, response, authorities, extra)


def parse_message(message):
    print(message)
    """
    Parse de uma mensagem
    :param message: Mensagem
    :return: Strings com os valores para as variáveis do objeto
             Response values, authorities values e extra values são listas de strings
    """
    message = message.replace("\n", "")
    fields = re.split(";|,", message)
    fields.remove("")

    message_id = fields[0]
    flags = fields[1]
    response_code = fields[2]
    num_response_values = fields[3]
    num_authorities_values = fields[4]
    num_extra_values = fields[5]
    name = fields[6]
    type = fields[7]

    response_values = list()
    authorities_values = list()
    extra_values = list()

    for i in range(1, int(num_response_values)+1):
        response_values.append(fields[7+i])

    for i in range(1, int(num_authorities_values)):
        authorities_values.append(fields[7+int(num_response_values)+i])

    for i in range(1, int(num_extra_values)):
        extra_values.append(fields[7+int(num_response_values)+int(num_authorities_values)+i])

    return (message_id, flags, response_code, num_response_values, num_authorities_values,
            num_extra_values, name, type, response_values, authorities_values, extra_values)


