# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 10/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de queries do tipo DNS
# Última atualização: Header

from .query import *

class DNS(Query):
    def __init__(self, message_id, flags, domain_name, type):
        super().__init__(message_id, flags, domain_name, type)

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return super().__repr__()


def string_to_dns(query):
    (message_id, flags, response_code, num_response_values, num_authorities_values,
     num_extra_values, name, type, response_values, authorities_values, extra_values) = parse_message(query)

    query = DNS(message_id, flags, name, type)
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
