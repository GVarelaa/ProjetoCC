# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 30/10/12
# Description: Implements a server, a Primary Server
# Last update: Added basic structure

from src.IO.parser import parser_df
from src.IO.parser import parser_st

class Server:
    def __init__(self, config_file_path):
        self.data_file_path = None
        self.domain = None
        self.secondary_servers = []
        self.default_domains = []
        self.log_file = None
        self.server_type = None
        self.root_servers_path = None
        # ficheiro de log global ? controlo de concorrência?

        self.parser_cf(config_file_path) # parser do ficheiro de configuração

        self.root_servers = parser_st(self.root_servers_path)
        self.db = parser_df(self.data_file_path)

    def __str__(self):
        return f"Base de Dados: {self.data_file_path}\nDomínio: {self.domain}\nServidores secundários: {self.secondary_servers}\nRoot Servers: {self.root_servers}\nFicheiro de Log: {self.log_file}"
    
    def __repr__(self):
        return f"Base de Dados: {self.data_file_path}\nDomínio: {self.domain}\nServidores secundários: {self.secondary_servers}\nRoot Servers: {self.root_servers}\nFicheiro de Log: {self.log_file}"

    def parser_cf(self, file_path):
        f = open(file_path, "r")

        for line in f:
            words = line.split()

            if len(words) > 0 and words[0][0] != '#':
                if len(words) == 3:
                    parameter = words[0]
                    value_type = words[1]
                    value = words[2]

                    if value_type == "DB":                       
                        self.data_file_path = value_type
                        self.domain = parameter

                    elif value_type == "SS":
                        self.secondary_servers.append(value)

                    elif value_type == "DD":
                        self.default_domains.append(value)

                    elif value_type == "ST" and parameter == "root":
                        self.root_servers_path = value

                    elif value_type == "LG":
                        if parameter == self.domain:
                            self.log_file = value


        f.close()




    def response_query(self, query): #objeto do tipo message
        header = query.header
        data = query.data
        flag = header.flags

        if 'Q' in flag:
            name = data.query_info.name
            type_of_value = data.query_info.type_of_value

            db_data = self.db[name, type_of_value]
            authorities_values = self.db[name, "NS"]

            if len(db_data) == 0:

            else:
                header.flags = "A"
                header.responde_code = "0" # alterar
                header.num_values = str(len(db_data))
                header.num_authorities = len(authorities_values)
                header.num_extra_values = None

                data.response_values = db_data
                data.authorities_values = authorities_values
                data.extra_values = None

            #header_response = Header(message_id, "A", response_code, num_values, )




p = Server("ConfigPrimary.txt")
print(p)