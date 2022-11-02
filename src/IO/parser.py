def validate_ip(ip_address):
    ip_parts = ip_address.split('.')
    ip_parts[-1] = (ip_parts[-1].split(':'))[0]

    port_bool = True
    if len(ip_address.split(':')) == 2:
        port = (ip_address.split(':'))[-1]
        if 1 > int(port) > 65000:
            port_bool = False

    return len(ip_parts) == 4 and all(0 <= int(part) < 256 for part in ip_parts) and port_bool

def parser_cf(file_path):
    f = open(file_path, "r")

    config = dict()

    for line in f:
        words = line.split()

        if len(words) > 0 and words[0][0] != '#':
            if len(words) == 3:
                parameter = words[0]
                value_type = words[1]
                value = words[2]

                if value_type == "DB":
                    if (parameter, value_type) not in config.keys():
                        config[(parameter, value_type)] = list()
                    config[(parameter, value_type)].append(value)

                elif value_type == "SP" and validate_ip(value):
                    if (parameter, value_type) not in config.keys():
                        config[(parameter, value_type)] = list()
                    config[(parameter, value_type)].append(value)

                elif value_type == "SS" and validate_ip(value):
                    if (parameter, value_type) not in config.keys():
                        config[(parameter, value_type)] = list()
                    config[(parameter, value_type)].append(value)

                elif value_type == "DD" and validate_ip(value):
                    if (parameter, value_type) not in config.keys():
                        config[(parameter, value_type)] = list()
                    config[(parameter, value_type)].append(value)

                elif value_type == "ST":
                    if (parameter, value_type) not in config.keys():
                        config[(parameter, value_type)] = list()
                    config[(parameter, value_type)].append(value)

                elif value_type == "LG":
                    if (parameter, value_type) not in config.keys():
                        config[(parameter, value_type)] = list()
                    config[(parameter, value_type)].append(value)


    f.close()

    return config

def parser_st(file_path):
    f = open(file_path, "r")

    servers = list()

    for line in f:
        if line[0] != "\n" and line[0] != "#":
            line = line.replace("\n", "")
            servers.append(line)

    f.close()

    return servers

def parser_df(file_path):
    f = open(file_path, "r")

    data = dict()

    #valores default
    ttl_default = 0
    sufix = ""

    for line in f:
        words = line.split()

        if len(words) > 0 and words[0][0] != '#':
            if len(words) == 3: #valores default
                if words[1] == "DEFAULT":
                    if words[0] == "TTL":
                        ttl_default = words[2]
                    elif words[0] == "@":
                        sufix = words[2]

            elif len(words) > 3:
                parameter = words[0]

                if "@" in words[0]:
                    parameter = words[0].rstrip(words[0][-1]) + sufix
                elif words[0][len(words[0])-1] != ".":
                    parameter += "." + sufix

                value_type = words[1]
                value = words[2]

                if words[3] == "TTL":
                    expiration = ttl_default
                else:
                    expiration = words[3]

                if len(words) == 5:
                    priority = words[4]
                else:
                    priority = 0

                if words[1] == "SOASP":
                    data[(parameter, value_type)] = (value, expiration)

                elif words[1] == "SOAADMIN":
                    data[(parameter, value_type)] = (value, expiration)

                elif words[1] == "SOASERIAL":
                    data[(parameter, value_type)] = (value, expiration)

                elif words[1] == "SOAREFRESH":
                    data[(parameter, value_type)] = (value, expiration)

                elif words[1] == "SOARETRY":
                    data[(parameter, value_type)] = (value, expiration)

                elif words[1] == "SOAEXPIRE":
                    data[(parameter, value_type)] = (value, expiration)

                elif words[1] == "NS":
                    if (parameter, value_type) not in data.keys():
                        data[(parameter, value_type)] = list()
                    data[(parameter, value_type)].append((value, expiration, priority))

                elif words[1] == "A" and validate_ip(value):
                    if (parameter, value_type) not in data.keys():
                        data[(parameter, value_type)] = list()
                    data[(parameter, value_type)].append((value, expiration, priority))

                elif words[1] == "CNAME":
                    data[(parameter, value_type)] = (value, expiration)

                elif words[1] == "MX":
                    if (parameter, value_type) not in data.keys():
                        data[(parameter, value_type)] = list()
                    data[(parameter, value_type)].append((value, expiration, priority))

                elif words[1] == "PTR" and validate_ip(words[0]):
                    if (parameter, value_type) not in data.keys():
                        data[(parameter, value_type)] = list()
                    data[(parameter, value_type)].append((value, expiration, priority))

    f.close()
    return data

    return data

#parser_df("dadossp.txt")
#parser_cf("config.txt")
#parser_st("st.txt")