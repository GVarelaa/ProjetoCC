# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 30/10/22
# Data da última atualização: 11/11/22
# Descrição: Implementação de um servidor
# Última atualização: Header

from log import Log


class Server:
    def __init__(self, domain, default_domains, root_servers, log_path):
        self.mode = None
        self.domain = domain
        self.default_domains = default_domains
        self.log_path = log_path
        self.log = Log(log_path) # Objeto do tipo log
        self.root_servers = root_servers
        self.cache = None

    def __str__(self):
        return f"Domínio: {self.domain}\nCache: {self.cache}\n" \
               f"Domínios por defeito: {self.default_domains}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log_path}"
    
    def __repr__(self):
        return f"Domínio: {self.domain}\nCache: {self.cache}\n" \
               f"Domínios por defeito: {self.default_domains}\nRoot Servers:" \
               f"{self.root_servers}\nFicheiro de Log: {self.log_path}"


    def parse_address(self, address):
        substrings = address.split(":")
        ip_address = substrings[0]

        if len(substrings) > 1:
            port = int(substrings[1])
        else:
            port = 5353 # porta default

        return (ip_address, port)


    def interpret_query(self, query): # interpret_query
        response_values = list()
        authorities_values = list()
        extra_values = list()

        if query.flags == "" and query.type == "252": # Query AXFR
            if(self.domain == query.domain_name):
                query.flags = "A"



                query.response_values.append(lines_number)
                return query
            else:
                return query
        else:
            response_values = self.cache.get_records_by_name_and_type(query.domain_name, query.type)

            if len(response_values) != 0:  # HIT
                authorities_values = self.cache.get_records_by_name_and_type(query.domain_name, "NS")
                extra_values = list()

                for record in response_values:
                    records = self.cache.get_records_by_name_and_type(record.value, "A")
                    extra_values += records

                for record in authorities_values:
                    records = self.cache.get_records_by_name_and_type(record.value, "A")
                    extra_values += records

                query.response_values = response_values
                query.authorities_values = authorities_values
                query.extra_values = extra_values

                if "R" in query.flags:
                    query.flags = "R+A"
                else:
                    query.flags = "A"

                return query

            else:  # MISS
                return None


