# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de queries
# Última atualização: Header

from resource_record import *
import re

class DNSMessage:
    def __init__(self, message_id, flags, domain_name, type):
        self.message_id = message_id
        self.flags = flags
        self.response_code = 0
        self.number_of_values = 0
        self.number_of_authorities = 0
        self.number_of_extra_values = 0
        self.domain_name = domain_name
        self.type = type
        self.response_values = list()
        self.authorities_values = list()
        self.extra_values = list()

    def __str__(self):
        return str(self.message_id) + " " + str(self.flags) + " " + str(self.response_code) + " " \
               + str(self.number_of_values) + " " + str(self.number_of_authorities) + " " \
               + str(self.number_of_extra_values) + " " + str(self.domain_name) + " " + str(self.type) + "\n" \
               + str(self.response_values) + "\n" + str(self.authorities_values) + "\n" + str(self.extra_values)

    def __repr__(self):
        return str(self.message_id) + " " + str(self.flags) + " " + str(self.response_code) + " " \
               + str(self.number_of_values) + " " + str(self.number_of_authorities) + " "  \
               + str(self.number_of_extra_values) + " " + str(self.domain_name) + " " + str(self.type) + "\n" \
               + str(self.response_values) + "\n" + str(self.authorities_values) + "\n" + str(self.extra_values)

    def to_string(self):
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
        (message_id, flags, response_code, num_response_values, num_authorities_values,
         num_extra_values, name, type, response_values, authorities_values, extra_values) = parse_message(query)

        query = DNSMessage(message_id, flags, name, type)
        query.response_code = int(response_code)
        query.number_of_values = int(num_response_values)
        query.number_of_authorities = int(num_authorities_values)
        query.number_of_extra_values = int(num_extra_values)
        # print(response_values)
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
        print("aqui")
        fields = message.split(";")

        if len(fields) < 2:
            return False

        fields.remove(fields[-1])

        header_fields = fields[0].split(",")
        data_fields = fields[1].split(",")

        if len(header_fields) < 6 or len(data_fields) < 2:
            return False

        return True


def parse_message(message):
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

