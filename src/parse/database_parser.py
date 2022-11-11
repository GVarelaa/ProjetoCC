# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 11/11/22
# Descrição: Parsing de ficheiros de dados de servidores primários
# Última atualização: Header

from parse.validation import *
from cache import *


def concatenate_suffix(suffix, name):
    if "@" in name:
        name = name.rstrip(name[-1]) + suffix

    elif name[-1] != ".":
        name += "." + suffix

    return name


def set_default_values(ttl_default, suffix, line):
    if line[0] == "TTL":
        ttl_default = line[2]

    elif line[0] == "@":
        suffix = line[2]

    return ttl_default, suffix


def set_ttl(ttl_default, word):
    if word == "TTL":
        ttl = ttl_default
    else:
        ttl = int(word)

    return ttl


def parser_database(server, file_content, origin):
    data = Cache(list())

    ttl_default = 0
    suffix = ""
    priority = -1

    file_content = file_content.split("\n")
    for line in file_content:
        words = line.split()

        if origin == "SP":
            words.remove(words[0])

        if len(words) > 0 and words[0][0] != '#':  # ignorar linhas vazias ou comentários
            if len(words) > 5:
                server.log.log_fl("Too many arguments!")

            # valores default
            if len(words) == 3 and words[1] == "DEFAULT":
                ttl_default, suffix = set_default_values(ttl_default, suffix, words)

            elif len(words) < 4:
                server.log.log_fl("Arguments missing!")

            else:
                parameter = concatenate_suffix(suffix, words[0])
                type = words[1]
                value = words[2]
                expiration = set_ttl(ttl_default, words[3])

                if len(words) == 5:
                    priority = int(words[4])

                if type == "SOASP":
                    record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                    data.add_entry(record)
                    server.soasp = value

                elif type == "SOAADMIN":
                    record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                    data.add_entry(record)
                    server.soaadmin = value

                elif type == "SOASERIAL":
                    record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                    data.add_entry(record)
                    server.soaserial = value

                elif type == "SOAREFRESH":
                    record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                    data.add_entry(record)
                    server.soarefresh = int(value)

                elif type == "SOARETRY":
                    record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                    data.add_entry(record)
                    server.soaretry = int(value)

                elif type == "SOAEXPIRE":
                    record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                    data.add_entry(record)
                    server.soaexpire = int(value)

                elif type == "NS":
                    record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                    data.add_entry(record)

                elif type == "A":
                    if validate_ip(value):
                        record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                        data.add_entry(record)
                    else:
                        server.log.log_fl("Invalid IP address!")

                elif type == "CNAME":
                    record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                    data.add_entry(record)

                elif type == "MX":
                    record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                    data.add_entry(record)

                elif type == "PTR":
                    if validate_ip(parameter):
                        record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                        data.add_entry(record)
                    else:
                        server.log.log_fl("Invalid IP address!")

        server.cache = data
