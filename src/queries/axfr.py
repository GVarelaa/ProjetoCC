from .query import *


class AXFR(Query):
    def __init__(self, message_id, domain_name):
        super().__init__(message_id, "", domain_name, "252")

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        return super().__repr__()


def string_to_axfr(query):
    (message_id, flags, response_code, num_response_values,
     num_authorities_values, num_extra_values, name, type) = parse_message(query)

    query = AXFR(message_id, name)
    query.flags = flags
    query.type = type
    query.response_code = int(response_code)
    query.number_of_values = int(num_response_values)
    query.number_of_authorities = int(num_authorities_values)
    query.number_of_extra_values = int(num_extra_values)
    # falta meter as listas
    return query
