# Data de criação: 13/11/22
# Data da última atualização: 13/11/22
# Descrição: Executa um servidor
# Última atualização: Timeout de string para inteiro

from parse.configuration_parser import *


def main():
    """
    Programa que corre um servidor
    """
    args = sys.argv
    config_path = args[1]  # Ficheiro de configuração
    port = int(args[2])  # Porta onde o servidor vai estar à escuta
    timeout = int(args[3])  # Tempo que o servidor vai esperar por uma resposta
    handles_recursion = int(args[4])  # Indica se o servidor aceita ou não o modo recursivo

    if handles_recursion == 1:
        handles_recursion = True
    elif handles_recursion == 0:
        handles_recursion = False

    if len(args) > 5:
        mode = args[5]  # Modo (Debug/Shy)
    else:
        mode = "debug"  # Modo debug por default

    try:
        server = parser_configuration(config_path, port, timeout, handles_recursion, mode)  # Parser dos dados
    except InvalidIPError:
        sys.stdout.write("Error running server configurations: Invalid IP address")
        return
    except InvalidPortError:
        sys.stdout.write("Error running server configurations: Invalid Port")
        return

    print(server.cache)

    if len(server.config["SS"].values()) != 0:  # Só recebe pedidos de ZT se for primário para algum domínio
        threading.Thread(target=server.sp_zone_transfer).start()

    for domain in server.config["SP"].keys():  # Vai pedir ZT para todos os seus servidores primários
        threading.Thread(target=server.ss_zone_transfer, args=(domain,)).start()

    threading.Thread(target=server.receive_queries).start()  # Thread para receber mensagens (socket UDP)


if __name__ == "__main__":
    main()
