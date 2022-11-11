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
    (message_id, flags, response_code, num_response_values,
     num_authorities_values, num_extra_values, name, type) = parse_message(query)

    query = DNS(message_id, flags, name, type)
    query.response_code = int(response_code)
    query.number_of_values = int(num_response_values)
    query.number_of_authorities = int(num_authorities_values)
    query.number_of_extra_values = int(num_extra_values)
    # falta meter as listas
    return query
