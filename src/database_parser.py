from validation import *
from cache import *


def concatenate_suffix(suffix, name):
    if "@" in name:
        name = name.rstrip(name[-1]) + suffix

    elif name[-1] != ".":
        name += "." + suffix

    return name


def set_default_values(line):
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


def parser_database(file_path, server):
    data = Cache()

    if file_path is not None:
        f = open(file_path, "r")

        ttl_default = 0
        suffix = ""
        priority = -1

        for line in f:
            words = line.split()

            if len(words) > 0 and words[0][0] != '#': # ignorar linhas vazias ou comentários
                if len(words) > 5:
                    server.log.log_fl("Too many arguments!")

                # valores default
                if len(words) == 3 and words[1] == "DEFAULT":
                        ttl_default, suffix = set_default_values(words)

                elif len(words) <= 4:
                    server.log.log_fl("Arguments missing!")

                else:
                    parameter = words[0]
                    concatenate_suffix(suffix, parameter)
                    type = words[1]
                    value = words[2]
                    expiration = set_ttl(ttl_default, words[3])

                    if len(words) == 5:
                        priority = int(words[4])

                    if words[1] == "SOASP":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif words[1] == "SOAADMIN":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif words[1] == "SOASERIAL":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif words[1] == "SOAREFRESH":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif words[1] == "SOARETRY":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif words[1] == "SOAEXPIRE":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif words[1] == "NS":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif words[1] == "A" and validate_ip(value):
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif words[1] == "CNAME":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif words[1] == "MX":
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

                    elif words[1] == "PTR" and validate_ip(words[0]):
                        record = ResourceRecord(parameter, type, value, expiration, priority, "FILE")
                        data.add_entry(record)

        f.close()

        server.cache = data

    return server
