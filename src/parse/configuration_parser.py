# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 11/11/22
# Descrição: Parsing de ficheiros de configuração de servidores
# Última atualização: Header

from parse.validation import *
from server.primary_server import *
from server.secondary_server import *
from parse.database_parser import *
from log import *


def parser_root_servers(file_path):
    f = open(file_path, "r")

    servers = list()

    for line in f:
        if line[0] != "\n" and line[0] != "#":
            line = line.replace("\n", "")
            servers.append(line)

    f.close()

    return servers


def parser_configuration(file_path, port, timeout, mode):
    if mode == "debug":
        mode_bool = True
    else:
        mode_bool = False

    domain = None
    data_path = None
    file_content = None
    primary_server = None
    secondary_servers = list()
    root_servers = list()
    default_domains = list()
    domain_log_path = None
    all_log_path = None

    f = open(file_path, "r")

    for line in f:
        line = line.split("#")[0]  # ignorar comentários
        words = line.split()

        if len(words) > 0:
            if len(words) == 3:
                if words[0] != "root" and words[0] != "all":
                    domain = words[0] + "."

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

                elif parameter == "all" and value_type == "LG":
                    all_log_path = value

                elif value_type == "LG":
                    domain_log_path = value

    f.close()

    domain_log = Log(domain_log_path, mode_bool, None)
    all_log = Log(all_log_path, mode_bool, None)

    if not validate_port(port):
        domain_log.log_sp("localhost", "invalid port")
        return None

    if mode != "shy" and mode != "debug":
        domain_log.log_sp("localhost", "invalid server mode")
        return None

    domain_log.log_st("localhost", port, timeout, mode)

    domain_log.log_ev("localhost", "conf-file-read", file_path)
    domain_log.log_ev("localhost", "log-file-create", domain_log_path)
    domain_log.log_ev("localhost", "log-file-create", all_log_path)

    if primary_server is None:
        server = PrimaryServer(domain, default_domains, root_servers, domain_log, all_log, port, mode, data_path, secondary_servers)
        parser_database(server, file_content, "FILE")
        domain_log.log_ev("localhost", "db-file-read", data_path)
    else:
        server = SecondaryServer(domain, default_domains, root_servers, domain_log, all_log, port, mode, primary_server)
        server.cache = Cache(list())

    return server
