# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 11/11/22
# Descrição: Implementação de logs
# Última atualização: Header

from datetime import datetime
import sys


class Log:
    def __init__(self, filepath, mode):
        self.filepath = filepath
        self.mode = mode
        self.fd = open(filepath, "a")

    def __str__(self):
        data = self.fd.read()
        return data

    def log_qe(self, ip_address, data):
        message = "QE " + ip_address + " " + data
        self.add_log(message)


    def log_qr(self, ip_address, data):
        message = "QR " + ip_address + " " + data
        self.add_log(message)

    def log_rp(self, ip_address, data):
        message = "RP " + ip_address + " " + data
        self.add_log(message)

    def log_rr(self, ip_address, data):
        message = "RR " + ip_address + " " + data
        self.add_log(message)

    def log_zt(self, ip_address, data, duration):
        if data == "SP" or data == "SS":
            message = "ZT " + ip_address + " " + data + " " + duration
            self.add_log(message)

    def log_ev(self, ip_address, event, event_data):
        message = "EV " + ip_address + " " + event + " " + event_data
        self.add_log(message)

    def log_er(self, ip_address, info):
        message = "ER " + ip_address + " " + info
        self.add_log(message)

    def log_ez(self, ip_address, data):
        if data == "SP" or data == "SS":
            message = "EZ " + ip_address + " " + data
            self.add_log(message)

    def log_fl(self, info):
        message = "FL 127.0.0.1 " + info
        self.add_log(message)

    def log_to(self, ip_address, info):
        message = "TO " + ip_address + " " + info
        self.add_log(message)

    def log_sp(self, ip_address, info):
        message = "SP " + ip_address + " " + info
        self.add_log(message)

    def log_st(self, ip_address, port, timeout, mode):
        if mode == "shy" or mode == "debug":
            message = "ST " + ip_address + " " + port + " " + timeout
            self.add_log(message)

    def add_log(self, message):
        dt = datetime.now().strftime("%d:%m:%Y.%H:%M:%S:%f")

        self.fd.write(dt + " " + message + "\n")
        if self.mode == True:
            sys.stdout.write(dt + " " + message + "\n")



