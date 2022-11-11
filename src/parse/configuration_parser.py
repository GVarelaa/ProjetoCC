# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 11/11/22
# Descrição: Parsing de ficheiros de configuração de servidores
# Última atualização: Header

from parse.validation import *
from server.primary_server import *
from server.secondary_server import *
from parse.database_parser import *


def parser_root_servers(file_path):
    f = open(file_path, "r")

    servers = list()

    for line in f:
        if line[0] != "\n" and line[0] != "#":
            line = line.replace("\n", "")
            servers.append(line)

    f.close()

    return servers


def parser_configuration(file_path, mode):
    f = open(file_path, "r")

    if mode == "debug":
        mode = True
    else:
        mode = False

    domain = None
    data_path = None
    file_content = None
    primary_server = None
    secondary_servers = list()
    root_servers = list()
    default_domains = list()
    log_path = None

    for line in f:
        words = line.split()

        if len(words) > 0 and words[0][0] != '#':
            if len(words) == 3:
                if words[0] != "root" and words[0] != "all":
                    domain = words[0]

                parameter = words[0]
                value_type = words[1]
                value = words[2]

                if value_type == "DB":
                    data_path = value
                    f = open(data_path, "r")
                    file_content = f.read()
                    f.close()

                elif value_type == "SP" and validate_ip(value):
                    primary_server = value

                elif value_type == "SS" and validate_ip(value):
                    secondary_servers.append(value)

                elif value_type == "DD" and validate_ip(value):
                    default_domains.append(value)

                elif value_type == "ST" and parameter == "root":
                    root_servers = parser_root_servers(value)

                elif value_type == "LG":
                    log_path = value

    f.close()

    if primary_server is None:
        server = PrimaryServer(domain, default_domains, root_servers, log_path, mode, data_path, secondary_servers)
        parser_database(server, file_content, "FILE")
    else:
        server = SecondaryServer(domain, default_domains, root_servers, log_path, mode, primary_server)

    return server
