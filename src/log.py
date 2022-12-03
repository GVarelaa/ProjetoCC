# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 13/11/22
# Descrição: Implementação de logs
# Última atualização: Added coments

from datetime import datetime
import sys
import threading


class Log:
    def __init__(self, file_paths, is_debug):
        """
        Construtor de um objeto Log
        :param domain_filepath: Diretoria do ficheiro de domínio
        :param is_debug: Modo de funcionamento (debug ou shy)
        """
        self.file_paths = file_paths  # Ficheiro de domínio
        self.is_debug = is_debug  # True -> print para stdout
        self.lock = threading.Lock()

    def __str__(self):
        """
        Devolve a representação em string do objeto Log
        """
        #data = self.domain_filepath.read() MUDAR
        return "FAZER"

    def log_qe(self, domain, ip_address, data):
        """
        Regista log de query enviada
        :param ip_address: Endereço IP
        :param data: Dados
        """
        message = "QE " + ip_address + " " + data
        self.add_log(domain, message)

    def log_qr(self, domain, ip_address, data):
        """
        Regista log de query recebida
        :param ip_address: Endereço IP
        :param data: Dados
        """
        message = "QR " + ip_address + " " + data                   
        self.add_log(domain, message)

    def log_rp(self, domain, ip_address, data):
        """
        Regista log de query resposta enviada
        :param ip_address: Endereço IP
        :param data: Dados
        """
        message = "RP " + ip_address + " " + data                   
        self.add_log(domain, message)

    def log_rr(self, domain, ip_address, data):
        """
        Regista log de query resposta recebida
        :param ip_address: Endereço IP
        :param data: Dados
        """
        message = "RR " + ip_address + " " + data                           
        self.add_log(domain, message)

    def log_zt(self, domain, ip_address, data, duration):
        """
        Regista log de inicio/conclusão de transferência de zona
        :param ip_address: Endereço IP
        :param data: Dados
        :param duration: Duração
        """
        message = "ZT " + ip_address + " " + data + " " + duration
        self.add_log(domain, message)

    def log_ev(self, domain, ip_address, event, event_data):
        """
        Regista log de um evento
        :param ip_address: Endereço IP
        :param event: Evento
        :param event_data: Dados do evento
        """
        message = "EV " + ip_address + " " + event + " " + event_data
        self.add_log(domain, message)

    def log_er(self, domain, ip_address, info):
        """
        Regista log da receção de um PDU que não foi codificado corretamente
        :param ip_address: Endereço IP
        :param info: Informação
        """
        message = "ER " + ip_address + " " + info  # ip_address - source, info - onde ocorreu o erro
        self.add_log(domain, message)

    def log_ez(self, domain, ip_address, data):
        """
        Regista log de um erro na transferência de zona
        :param ip_address: Endereço IP
        :param data: Dados
        """
        message = "EZ " + ip_address + " " + data  # data - papel do servidor local
        self.add_log(domain, message)

    def log_fl(self, domain, entry, info):
        """
        Regista log de um erro detetado no funcionamento interno de um componente
        :param entry: Entrada
        :param info: Informação
        """
        message = "FL 127.0.0.1 | Entry: " + entry + " | " + info  # Info - razão (erros de parsing, erros na descodificação, etc)
        self.add_log(domain, message)

    def log_to(self, domain, ip_address, info):
        """
        Regista log de um timeout
        :param ip_address: Endereço IP
        :param info: Informação
        :return:
        """
        message = "TO " + ip_address + " " + info  # Info - tipo de timeout (ex: numa resposta a query, ou a tentar conectar ao SP para ZT)
        self.add_log(domain, message)

    def log_sp(self, domain, ip_address, info):
        """
        Regista log da paragem de execução de um componente
        :param ip_address: Endereço IP
        :param info: Informação
        """
        message = "SP " + ip_address + " " + info               
        self.add_log(domain, message)

    def log_st(self, domain, ip_address, port, timeout, mode):
        """
        Regista log de início da execução de um componente
        :param ip_address: Endereço de IP
        :param port: Porta de atendimento
        :param timeout: Valor de timeout
        :param mode: Modo de funcionamento
        """
        if mode == "shy" or mode == "debug":
            message = "ST " + ip_address + " " + port + " " + timeout + " " + mode
            self.add_log(domain, message)

    # Method called by the others
    def add_log(self, domain, message):
        """
        Regista log nos ficheiros das variáveis de instância
        :param message: Mensagem a ser registada
        """
        if domain in self.file_paths.keys():
            self.lock.acquire()

            domain_fd = open(self.file_paths[domain], "a")
            dt = datetime.now().strftime("%d:%m:%Y.%H:%M:%S:%f")

            domain_fd.write(dt + " " + message + "\n")

            if self.is_debug:
                sys.stdout.write(dt + " " + message + "\n")

            domain_fd.close()

            self.lock.release()



