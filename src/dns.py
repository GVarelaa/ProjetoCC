class DNS:
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
               + str(self.number_of_values) + " " + str(self.number_of_authorities) + " " + str(self.number_of_extra_values) + " " \
               + str(self.domain_name) + " " + str(self.type) + "\n" \
               + str(self.response_values) + "\n" + str(self.authorities_values) + "\n" + str(self.extra_values)

    def __repr__(self):
        return str(self.message_id) + " " + str(self.flags) + " " + str(self.response_code) + " " \
               + str(self.number_of_values) + " " + str(self.number_of_authorities) + " " + str(self.number_of_extra_values) + " "\
               + str(self.domain_name) + " " + str(self.type) + "\n" \
               + str(self.response_values) + "\n" + str(self.authorities_values) + "\n" + str(self.extra_values)


    def dns_to_string(self):
        string = str(self.message_id) + "," + str(self.flags) + "," + str(self.response_code) + "," \
                 + str(self.number_of_values) + "," + str(self.number_of_authorities) + "," + str(self.number_of_values) + ";"\
                 + str(self.domain_name) + "," + str(self.type) + ";\n"

        for record in self.extra_values:
            string += record.resource_record_to_string() +","

        string = string[:-1] + ";"

        for record in self.authorities_values:
            string += record.resource_record_to_string() + ","

        string = string[:-1] + ";"

        for record in self.extra_values:
            string += record.resource_record_to_string() + ","

        string = string[:-1] + ";"

        return string


def string_to_dns(query):
    (message_id, flags, response_code, num_response_values,
     num_authorities_values, num_extra_values, name, type) = parse_message(query)

    query = DNS(message_id, flags, name, type)
    query.response_code = int(response_code)
    query.number_of_values = int(num_response_values)
    query.number_of_authorities = int(num_authorities_values)
    query.number_of_extra_values = int(num_extra_values)
    #falta meter as listas
    return query


def parse_message(message):
    fields = message.split(";")
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

    return (message_id, flags, response_code, num_response_values,
            num_authorities_values, num_extra_values, name, type)
