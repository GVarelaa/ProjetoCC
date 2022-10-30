# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 30/10/12
# Description: Implements a server, a Primary Server
# Last update: Added basic structure

class PrimaryServer:
    def __init__(self, config_file_path):
        self.__data_file_path = None
        self.__domain = None
        self.__secondary_servers = []
        self.__default_domains = []
        self.__root_servers = []
        self.__log_file = None
        # ficheiro de log global ? controlo de concorrência?
        
        self.parser_cf(config_file_path)

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
                        self.__root_servers.append(value)

                    elif value_type == "LG":
                        if parameter == self.__domain:
                            self.__log_file = value


        f.close()


    def interpretQuery(self, query):
        print('prim')

p = PrimaryServer("ConfigPrimary.txt")
print(p)