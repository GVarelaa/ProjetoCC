# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 11/11/22
# Descrição: Parsing de ficheiros de dados de servidores primários
# Última atualização: Header

from parse.validation import *
from cache import *


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


def replace_email(email):
    parts = email.split("\\.")
    parts[-1] = parts[-1].replace(".", "@", 1)
    email = '.'.join(parts)

    return email


def concatenate_suffix_aux(suffix, name):
    if name[-1] != ".":
        name += "." + suffix

    return name


def concatenate_suffix(type, suffix, parameter, value):
    if type == "SOASERIAL" or type == "SOAREFRESH" or type == "SOARETRY" or type == "SOAEXPIRE" or type == "A":
        parameter = concatenate_suffix_aux(suffix, parameter)

    elif type == "SOASP" or type == "NS" or type == "CNAME" or type == "MX" or type == "SOAADMIN":
        if type == "SOAADMIN":
            value = replace_email(value)

        parameter = concatenate_suffix_aux(suffix, parameter)
        value = concatenate_suffix_aux(suffix, value)

    elif type == "PTR":
        value = concatenate_suffix_aux(suffix, value)

    return parameter, value


def parser_database(server, file_content, origin):
    data = Cache(list())

    ttl_default = 0
    suffix = ""
    priority = -1
    names_list = list()

    file_content = file_content.split("\n")

    for line in file_content:
        line = line.split("#")[0]  # ignorar comentários

        if suffix != "":
            line = line.replace("@", suffix)

        words = line.split()

        if origin == "SP":
            words.remove(words[0])

        if len(words) > 0:  # ignorar linhas vazias
            if len(words) > 5:
                server.domain_log.log_fl("Too many arguments")

            # valores default
            if len(words) == 3 and words[1] == "DEFAULT":
                ttl_default, suffix = set_default_values(ttl_default, suffix, words)

            elif len(words) < 4:
                server.domain_log.log_fl("Arguments missing")

            else:
                type = words[1]
                parameter, value = concatenate_suffix(type, suffix, words[0], words[2])
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
                        names_list.append(parameter)
                    else:
                        server.log.log_fl("Invalid IP address")

                elif type == "CNAME":
                    if value in names_list:
                        record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                        data.add_entry(record)
                    else:
                        server.log.log_fl("Name not found")

                elif type == "MX":
                    record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                    data.add_entry(record)

                elif type == "PTR":
                    if validate_ip(parameter):
                        record = ResourceRecord(parameter, type, value, expiration, priority, origin)
                        data.add_entry(record)
                    else:
                        server.log.log_fl("Invalid IP address")

                else:
                    server.log.log_fl("Invalid type")

        server.cache = data
