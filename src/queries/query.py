# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de queries
# Última atualização: Header

from resource_record import *

class Query:
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

    def query_to_string(self):
        string = str(self.message_id) + "," + str(self.flags) + "," + str(self.response_code) + "," \
                 + str(self.number_of_values) + "," + str(self.number_of_authorities) + "," \
                 + str(self.number_of_values) + ";" + str(self.domain_name) + "," + str(self.type) + ";\n"

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


def parse_message(message):
    fields = message.split(";")
    fields.remove(fields[-1])

    header_fields = fields[0].split(",")
    data_fields = fields[1].split(",")

    message_id = header_fields[0]
    flags = header_fields[1]
    response_code = header_fields[2]
    num_response_values = header_fields[3]
    num_authorities_values = header_fields[4]
    num_extra_values = header_fields[5]

    name = data_fields[0]
    type = data_fields[1]

    response_values = list()
    authorities_values = list()
    extra_values = list()

    if len(fields) > 2:
        response_values = fields[2]
        response_values = response_values.replace("\n", "")
        response_values = response_values.split(",")

    if len(fields) > 3:
        authorities_values = fields[3]
        authorities_values = authorities_values.replace("\n", "")
        authorities_values = authorities_values.split(",")

    if len(fields) > 4:
        extra_values = fields[4]
        extra_values = extra_values.replace("\n", "")
        extra_values = extra_values.split(",")

    return (message_id, flags, response_code, num_response_values, num_authorities_values,
            num_extra_values, name, type, response_values, authorities_values, extra_values)