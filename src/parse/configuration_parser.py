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
    config = dict()
    logs = dict()

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
                    words[0] = words[0] + "."

                parameter = words[0]
                value_type = words[1]
                value = words[2]

                if value_type == "DB":
                    if value_type not in config.keys():
                        config[value_type] = dict()

                    config[value_type][parameter] = value

                elif value_type == "SP":
                    if not validate_ip(value):
                        if is_debug:
                            sys.stdout.write("Error running server configurations: Invalid IP address")
                        return None

                    if value_type not in config.keys():
                        config[value_type] = dict()

                    config[value_type][parameter] = value

                elif value_type == "SS":
                    if not validate_ip(value):
                        if is_debug:
                            sys.stdout.write("Error running server configurations: Invalid IP address")
                        return None

                    if value_type not in config.keys():
                        config[value_type] = dict()

                        if parameter not in config[value_type].keys():
                            config[value_type][parameter] = list()
                            config[value_type][parameter].append(value)

                elif value_type == "DD":
                    if not validate_ip(value):
                        if is_debug:
                            sys.stdout.write("Error running server configurations: Invalid IP address")
                        return None

                    if value_type not in config.keys():
                        config[value_type] = dict()

                        if parameter not in config[value_type].keys():
                            config[value_type][parameter] = list()
                            config[value_type][parameter].append(value)

                elif value_type == "ST" and parameter == "root":
                    if value_type not in config.keys():
                        config[value_type] = dict()

                    config[value_type][parameter] = parser_root_servers(value)

                elif value_type == "LG":
                    if value_type not in config.keys():
                        config[value_type] = dict()

                    config[value_type][parameter] = value
                    logs[parameter] = Log(parameter, is_debug)

                    # resolver quando o log do dominio é enviado antes do all
                    if "all" in config[value_type].keys():
                        logs["all"].log_ev("localhost", "log-file-create", value)

    f.close()

    if mode != "shy" and mode != "debug":
        return None

    if not validate_port(port):
        logs["all"].log_sp("localhost", "invalid port")
        return None

    logs["all"].log_st("localhost", port, timeout, mode)
    logs["all"].log_ev("localhost", "conf-file-read", file_path)

    server = Server(config, logs, port)
    parser_database_caller(server)

    return server
