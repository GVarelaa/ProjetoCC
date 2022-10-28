def parser(file_path):
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



(db, sp, ss, dd, st, lg) = parser("ola.txt")

print(db)
print(sp)
print(ss)
print(dd)
print(st)
print(lg)