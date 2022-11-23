# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 19/11/22
# Descrição: Parsing de ficheiros de configuração de servidores
# Última atualização: Documentação

from parse.validation import *
from server.primary_server import *
from server.secondary_server import *
from parse.database_parser import *
from log import *


def parser_root_servers(file_path):
    """
    Parsing do ficheiro dos root servers
    :param file_path: Ficheiro de root servers
    :return: Lista dos root servers
    """
    f = open(file_path, "r")

    servers = list()

    for line in f:
        if line[0] != "\n" and line[0] != "#":
            line = line.replace("\n", "")
            servers.append(line)

    f.close()

    return servers


def parser_configuration(file_path, port, timeout, mode):
    """
    Função responsável pelo parse dos ficheiros de configuração
    :param file_path: Ficheiro de configuração
    :param port: Porta
    :param timeout: Timeout
    :param mode: Modo
    :return: Servidor
    """
    domain = None
    data_path = None
    primary_server = None
    secondary_servers = list()
    root_servers = list()
    default_domains = list()
    domain_log_path = None
    all_log_path = None
    is_debug = False

    if mode == "debug":
        is_debug = True

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

                elif value_type == "SP":
                    if not validate_ip(value):
                        if is_debug:
                            sys.stdout.write("Error running server configurations: Invalid IP address")
                        return None

                    primary_server = value

                elif value_type == "SS":
                    if not validate_ip(value):
                        if is_debug:
                            sys.stdout.write("Error running server configurations: Invalid IP address")
                        return None

                    secondary_servers.append(value)

                elif value_type == "DD":
                    if not validate_ip(value):
                        if is_debug:
                            sys.stdout.write("Error running server configurations: Invalid IP address")
                        return None

                    default_domains.append(value)

                elif value_type == "ST" and parameter == "root":
                    root_servers = parser_root_servers(value)

                elif parameter == "all" and value_type == "LG":
                    all_log_path = value

                elif value_type == "LG":
                    domain_log_path = value

    f.close()

    if mode != "shy" and mode != "debug":
        return None

    log = Log(domain_log_path, all_log_path, is_debug)

    if not validate_port(port):
        log.log_sp("localhost", "invalid port")
        return None

    log.log_st("localhost", port, timeout, mode)
    log.log_ev("localhost", "conf-file-read", file_path)
    log.log_ev("localhost", "log-file-create", domain_log_path)
    log.log_ev("localhost", "log-file-create", all_log_path)

    if primary_server is None:
        server = PrimaryServer(domain, default_domains, root_servers, log, port, mode, data_path, secondary_servers)
        parser_database(server, data_path)
    else:
        server = SecondaryServer(domain, default_domains, root_servers, log, port, mode, primary_server)
        server.cache = Cache(list())

    return server
