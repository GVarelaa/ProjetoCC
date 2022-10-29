def parser_cf(file_path):
    f = open(file_path, "r")

    db = list()
    sp = list()
    ss = list()
    dd = list()
    st = list()
    lg = list()

    for line in f:

        words = line.split()

        if len(words) >= 3 and words[0][0] != '#':
            parametro = words[0]
            valor = words[2]
            if words[1] == "DB":
                db.append((parametro, valor))
            elif words[1] == "SP":
                sp.append((parametro, valor))
            elif words[1] == "SS":
                ss.append((parametro, valor))
            elif words[1] == "DD":
                dd.append((parametro, valor))
            elif words[1] == "ST":
                st.append((parametro, valor))
            elif words[1] == "LG":
                lg.append((parametro, valor))


    f.close()

    return(db, sp, ss, dd, st, lg)


def parser_df(file_path):
    f = open(file_path, "r")

    data = dict()
    ttl = 0
    prefix = ""

    for line in f:
        words = line.split()

        if words[0][0] != '#':
            if len(words) >= 3:
                if words[1] == "DEFAULT": #valores default
                    if words[0] == "TTL":
                        ttl_default = words[2]
                    elif words[0] == "@":
                        prefix = words[2].rstrip(words[2][-1])

                parameter = words[0]

                if "@" in words[0]:
                    parameter = words[0].rstrip(words[0][-1]) + prefix

                elif words[0][len(words[0])-1] != ".":
                    parameter += "." + prefix

                value_type = words[1]

                if words[2][len(words[2])-1] == ".":
                    value = words[2].rstrip(words[2][-1])
                else:
                    value = words[2]

                expiration = ttl

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
                    try:
                        data[(parameter, value_type)].append((words[2], words[3], priority))
                    except KeyError:
                        data[(parameter, value_type)] = list()
                        data[(parameter, value_type)].append((words[2], words[3], priority))

                elif words[1] == "A":
                    try:
                        data[(parameter, value_type)].append((words[2], words[3], priority))
                    except KeyError:
                        data[(parameter, value_type)] = list()
                        data[(parameter, value_type)].append((words[2], words[3], priority))

                elif words[1] == "CNAME":
                    data[(parameter, value_type)] = (value, expiration)

                elif words[1] == "MX":
                    try:
                        data[(parameter, value_type)].append((words[2], words[3], priority))
                    except KeyError:
                        data[(parameter, value_type)] = list()
                        data[(parameter, value_type)].append((words[2], words[3], priority))

                elif words[1] == "PTR":
                    try:
                        data[(parameter, value_type)].append((words[2], words[3], priority))
                    except KeyError:
                        data[(parameter, value_type)] = list()
                        data[(parameter, value_type)].append((words[2], words[3], priority))

    print(data)
    f.close()

parser_df("dadossp.txt")