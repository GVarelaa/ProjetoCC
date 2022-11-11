# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 02/11/22
# Data da última atualização: 11/11/22
# Descrição: Validação de endereços IP e portas
# Última atualização: Header

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