from primary_server import *
from secondary_server import *

def validate_port(port):
    return 1 < int(port) < 65000


def validate_ip(ip_address):
    ip_parts = ip_address.split('.')
    ip_parts[-1] = (ip_parts[-1].split(':'))[0]

    length = len(ip_address.split(':'))
    port_bool = True

    if length > 2:
        port_bool = False

    elif length == 2:
        port = (ip_address.split(':'))[-1]
        port_bool = validate_port(port)

    return len(ip_parts) == 4 and all(0 <= int(part) < 256 for part in ip_parts) and port_bool


def parser_configuration(file_path):
    f = open(file_path, "r")

    domain = None
    data_path = None
    primary_server = None
    secondary_servers = list()
    default_domains = list()
    root_path = None
    log_path = None

    for line in f:
        words = line.split()

        if len(words) > 0 and words[0][0] != '#':
            if len(words) == 3:
                if words[0] != "root" and words[0] != "all":
                    domain = words[0]

                parameter = words[0]
                value_type = words[1]
                value = words[2]

                if value_type == "DB":
                    data_path = value

                elif value_type == "SP" and validate_ip(value):
                    primary_server = value

                elif value_type == "SS" and validate_ip(value):
                    secondary_servers.append(value)

                elif value_type == "DD" and validate_ip(value):
                    default_domains.append(value)

                elif value_type == "ST" and parameter == "root":
                    root_path = value

                elif value_type == "LG":
                    log_path = value

    f.close()

    if primary_server is not None:
        server = PrimaryServer(domain, default_domains, data_path, root_path, log_path, secondary_servers)
    else:
        server = SecondaryServer(domain, default_domains, data_path, root_path, log_path, primary_server)

    return server
