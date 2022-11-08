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
               + str(self.number_of_values) + " " + str(self.number_of_authorities) + " " + str(self.number_of_extra_values) \
               + str(self.domain_name) + " " + str(self.type) + "\n" \
               + str(self.response_values) + "\n" + str(self.authorities_values) + "\n" + str(self.extra_values) + "\n"

    def __repr__(self):
        return str(self.message_id) + " " + str(self.flags) + " " + str(self.response_code) + " " \
               + str(self.number_of_values) + " " + str(self.number_of_authorities) + " " + str(self.number_of_extra_values) \
               + str(self.domain_name) + " " + str(self.type) + "\n" \
               + str(self.response_values) + "\n" + str(self.authorities_values) + "\n" + str(self.extra_values) + "\n"


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

