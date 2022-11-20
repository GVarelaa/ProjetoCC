# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 11/11/22
# Descrição: Parsing de ficheiros de dados de servidores primários
# Última atualização: Header

from parse.validation import *
from cache import *


def set_default_values(server, ttl_default, suffix, line):
    if line[0] == "TTL":
        if line[2].isnumeric():
            ttl_default = line[2]
        else:
            server.domain_log.log_fl("Invalid value for TTL")

    elif line[0] == "@":
        suffix = line[2]

    return ttl_default, suffix


def set_ttl(ttl_default, word):
    if word == "TTL":
        ttl = ttl_default
    elif word.isnumeric():
        ttl = int(word)
    else:
        ttl = -1

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


def parser_database(server, file_path):
    server.log.log_ev("localhost", "db-file-read", file_path)

    data = Cache(list())

    if file_path is not None:
        f = open(file_path, "r")

        ttl_default = 0
        suffix = ""
        priority = -1
        names_list = list()

        for line in f:
            entry = line.split("#")[0]  # ignorar comentários

            if suffix != "":
                entry = entry.replace("@", suffix)

            words = entry.split()

            if len(words) > 0:  # ignorar linhas vazias
                if len(words) < 3:
                    server.log.log_fl(entry.replace("\n", ""), "Arguments missing")

                elif words[1] == "DEFAULT":
                    if len(words) == 3:
                        ttl_default, suffix = set_default_values(server, ttl_default, suffix, words)

                    else:
                        server.log.log_fl(entry.replace("\n", ""), "Too many arguments")

                elif len(words) > 5:
                    server.log.log_fl(entry.replace("\n", ""), "Too many arguments")

                elif len(words) < 4:
                    server.log.log_fl(entry.replace("\n", ""), "Arguments missing")

                else:
                    type = words[1]
                    parameter, value = concatenate_suffix(type, suffix, words[0], words[2])
                    expiration = set_ttl(ttl_default, words[3])

                    if expiration == -1:
                        server.log.log_fl(entry.replace("\n", ""), "Invalid value for TTL")
                        continue

                    if len(words) == 5:
                        if words[4].isnumeric() and 0 <= int(words[4]) < 256:
                            priority = int(words[4])
                        else:
                            server.log.log_fl(entry.replace("\n", ""), "Invalid value for priority")
                            continue

                    if type == "SOASP":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif type == "SOAADMIN":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif type == "SOASERIAL":
                        if value.isnumeric():
                            record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                            data.add_entry(record)
                        else:
                            server.log.log_fl(entry.replace("\n", ""), "Invalid value for SOASERIAL")

                    elif type == "SOAREFRESH":
                        if value.isnumeric():
                            record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                            data.add_entry(record)
                        else:
                            server.log.log_fl(entry.replace("\n", ""), "Invalid value for SOAREFRESH")

                    elif type == "SOARETRY":
                        if value.isnumeric():
                            record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                            data.add_entry(record)
                        else:
                            server.log.log_fl(entry.replace("\n", ""), "Invalid value for SOARETRY")

                    elif type == "SOAEXPIRE":
                        if value.isnumeric():
                            record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                            data.add_entry(record)
                        else:
                            server.log.log_fl(entry.replace("\n", ""), "Invalid value for SOAEXPIRE")

                    elif type == "NS":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif type == "A":
                        if validate_ip(value):
                            record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                            data.add_entry(record)
                            names_list.append(parameter)
                        else:
                            server.log.log_fl(entry.replace("\n", ""), "Invalid IP address")

                    elif type == "CNAME":
                        if value in names_list:
                            record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                            data.add_entry(record)
                        else:
                            server.log.log_fl(entry.replace("\n", ""), "Name not found")

                    elif type == "MX":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif type == "PTR":
                        if validate_ip(parameter):
                            record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                            data.add_entry(record)
                        else:
                            server.log.log_fl(entry.replace("\n", ""), "Invalid IP address")

                    else:
                        server.log.log_fl(entry.replace("\n", ""), "Invalid type")

        f.close()

        server.cache = data
