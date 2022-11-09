from validation import *
from cache import *


def parser_database(file_path):
    if file_path is None:
        return Cache()

    f = open(file_path, "r")

    data = Cache()

    #valores default
    ttl_default = 0
    suffix = ""

    for line in f:
        words = line.split()

        if len(words) > 0 and words[0][0] != '#':
            if len(words) == 3: #valores default
                if words[1] == "DEFAULT":
                    if words[0] == "TTL":
                        ttl_default = words[2]
                    elif words[0] == "@":
                        suffix = words[2]

            elif len(words) > 3:
                parameter = words[0]

                if "@" in words[0]:
                    parameter = words[0].rstrip(words[0][-1]) + suffix
                elif words[0][len(words[0])-1] != ".":
                    parameter += "." + suffix

                value_type = words[1]
                value = words[2]

                if words[3] == "TTL":
                    expiration = ttl_default
                else:
                    expiration = int(words[3])

                if len(words) == 5:
                    priority = int(words[4])
                else:
                    priority = int("0")

                if words[1] == "SOASP":
                    record = ResourceRecord(parameter, value_type, value, expiration, -1, "FILE")
                    data.add_entry(record)

                elif words[1] == "SOAADMIN":
                    record = ResourceRecord(parameter, value_type, value, expiration, -1, "FILE")
                    data.add_entry(record)

                elif words[1] == "SOASERIAL":
                    record = ResourceRecord(parameter, value_type, value, expiration, -1, "FILE")
                    data.add_entry(record)

                elif words[1] == "SOAREFRESH":
                    record = ResourceRecord(parameter, value_type, value, expiration, -1, "FILE")
                    data.add_entry(record)

                elif words[1] == "SOARETRY":
                    record = ResourceRecord(parameter, value_type, value, expiration, -1, "FILE")
                    data.add_entry(record)

                elif words[1] == "SOAEXPIRE":
                    record = ResourceRecord(parameter, value_type, value, expiration, -1, "FILE")
                    data.add_entry(record)

                elif words[1] == "NS":
                    record = ResourceRecord(parameter, value_type, value, expiration, priority, "FILE")
                    data.add_entry(record)

                elif words[1] == "A" and validate_ip(value):
                    record = ResourceRecord(parameter, value_type, value, expiration, priority, "FILE")
                    data.add_entry(record)

                elif words[1] == "CNAME":
                    record = ResourceRecord(parameter, value_type, value, expiration, priority, "FILE")
                    data.add_entry(record)

                elif words[1] == "MX":
                    record = ResourceRecord(parameter, value_type, value, expiration, priority, "FILE")
                    data.add_entry(record)

                elif words[1] == "PTR" and validate_ip(words[0]):
                    record = ResourceRecord(parameter, value_type, value, expiration, priority, "FILE")
                    data.add_entry(record)

    f.close()

    return data