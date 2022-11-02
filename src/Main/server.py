# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 30/10/12
# Description: Implements a server, a Primary Server
# Last update: Added basic structure

from src.IO.parser import parser_df
from src.IO.parser import parser_st

class Server:
    def __init__(self, config_file_path):
        self.__data_file_path = None
        self.__domain = None
        self.__secondary_servers = []
        self.__default_domains = []
        self.__log_file = None
        self.__server_type = None
        self.__root_servers_path = None
        # ficheiro de log global ? controlo de concorrência?

        self.parser_cf(config_file_path) # parser do ficheiro de configuração

        self.__root_servers = parser_st(self.__root_servers_path)
        self.__db = parser_df(self.__data_file_path)

    def __str__(self):
        return f"Base de Dados: {self.__data_file_path}\nDomínio: {self.__domain}\nServidores secundários: {self.__secondary_servers}\nRoot Servers: {self.__root_servers}\nFicheiro de Log: {self.__log_file}"
    
    def __repr__(self):
        return f"Base de Dados: {self.__data_file_path}\nDomínio: {self.__domain}\nServidores secundários: {self.__secondary_servers}\nRoot Servers: {self.__root_servers}\nFicheiro de Log: {self.__log_file}"

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
                        self.__data_file_path = value_type
                        self.__domain = parameter

                    elif value_type == "SS":
                        self.__secondary_servers.append(value)

                    elif value_type == "DD":
                        self.__default_domains.append(value)

                    elif value_type == "ST" and parameter == "root":
                        self.__root_servers_path = value

                    elif value_type == "LG":
                        if parameter == self.__domain:
                            self.__log_file = value


        f.close()




    def response_query(self, query): #objeto do tipo message
        header = query.get_header()
        flag = header.get_flags()

        if 'Q' in flag:
            header = query.get_header()
            data = query.get_data()

            query_info = data.get_query_info()
            name = query_info.get_name()
            type_of_value = query_info.get_type_of_value()

            db_data = self.__db[name, type_of_value]

            if len(db_data) == 0:

            else:
                authorities_values = self.__db[name, "NS"]

                header.__flags = "A"
                header.__responde_code = "0" # alterar
                header.__num_values = str(len(db_data))
                header.__num_authorities = len(authorities_values)
                header.__num_extra_values = None

                data.__response_values = db_data
                data.__authorities_values = authorities_values
                data.__extra_values = None

            #header_response = Header(message_id, "A", response_code, num_values, )




p = Server("ConfigPrimary.txt")
print(p)