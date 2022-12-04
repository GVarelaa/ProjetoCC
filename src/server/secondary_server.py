# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 08/11/22
# Data da última atualização: 11/11/22
# Descrição: Representação de um servidor secundário
# Última atualização: Documentação

import random
import socket
import time
import threading
from server.server import Server
from dns_message import *
import select


class SecondaryServer(Server):
    def __init__(self, domain, default_domains, root_servers, log, port, mode, primary_server):
        """
        Construtor de um objeto SecondaryServer
        :param domain: Nome do domínio
        :param default_domains: Lista de domínios por defeito
        :param root_servers: Lista de root servers
        :param log: Objeto Log
        :param port: Porta
        :param mode: Modo
        :param primary_server: Endereço IP do servidor primário
        """
        super().__init__(domain, default_domains, root_servers, log, port, mode)
        self.primary_server = primary_server

    def __str__(self):
        """
        Devolve a representação em string do objeto SecondaryServer
        :return: String
        """
        return super().__str__() + f"Servidor primário: {self.primary_server}\n"

    def __repr__(self):
        """
        Devolve a representação oficial em string do objeto SecondaryServer
        :return: String
        """
        return super().__str__() + f"Servidor primário: {self.primary_server}\n"

    def zone_transfer(self):
        """
        Executa a transferència de zona
        """
        while True:
            self.zone_transfer_process()
            #meter soarefresh default
            soarefresh = int(self.cache.get_records_by_name_and_type(self.domain, "SOAREFRESH")[0].value)
            time.sleep(soarefresh)

