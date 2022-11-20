# Autores: Gabriela Cunha, Guilherme Varela e Miguel Braga
# Data de criação: 29/10/22
# Data da última atualização: 13/11/22
# Descrição: Implementação de logs
# Última atualização: Added coments

from datetime import datetime
import sys
import threading


class Log:
    def __init__(self, domain_filepath, all_filepath, is_debug):
        self.domain_filepath = domain_filepath  # Name of the domain log file
        self.all_filepath = all_filepath  # Name of the all log file
        self.is_debug = is_debug  # True means DEBUG mode -> also print to stdout
        self.lock = threading.Lock()

    def __str__(self):
        data = self.filepath.read()
        return data

    def log_qe(self, ip_address, data):                                     # Query was sent to the given address
        message = "QE " + ip_address + " " + data
        self.add_log(message)

    def log_qr(self, ip_address, data):                                     # Query was received from the given address
        message = "QR " + ip_address + " " + data                   
        self.add_log(message)                   

    def log_rp(self, ip_address, data):                                     # Response was sent to the given address
        message = "RP " + ip_address + " " + data                   
        self.add_log(message)                   

    def log_rr(self, ip_address, data):                                     # Response was received from the given address
        message = "RR " + ip_address + " " + data                           
        self.add_log(message)                   

    def log_zt(self, ip_address, data, duration):                           # Zone transfer process to the other end (ip) was successfully terminated
        message = "ZT " + ip_address + " " + data + " " + duration
        self.add_log(message)

    def log_ev(self, ip_address, event, event_data):                        # Misc event in the component
        message = "EV " + ip_address + " " + event + " " + event_data
        self.add_log(message)

    def log_er(self, ip_address, info):                                     # Decoding error
        message = "ER " + ip_address + " " + info                               # ip_address - source
        self.add_log(message)                                                   # info - where the error was, what was possible to decode

    def log_ez(self, ip_address, data):                                     # Zone transfer error
        message = "EZ " + ip_address + " " + data                           # data - role of the local server
        self.add_log(message)

    def log_fl(self, entry, info):                                                 # Internal server error
        message = "FL 127.0.0.1 | Entry: " + entry + " | " + info                                        # Info - reason (parsing errors, decoding errors, etc)
        self.add_log(message)               

    def log_to(self, ip_address, info):                                     # Timeout detected in the response of the server identified by ip
        message = "TO " + ip_address + " " + info                               # Info - type of timeout (ex: in a response to a query, or trying to contact SP for ZT)
        self.add_log(message)               

    def log_sp(self, ip_address, info):                                     # Component (server) stopped
        message = "SP " + ip_address + " " + info               
        self.add_log(message)               


    def log_st(self, ip_address, port, timeout, mode):                      # Component (server) started
        if mode == "shy" or mode == "debug":
            message = "ST " + ip_address + " " + port + " " + timeout + " " + mode
            self.add_log(message)

    # Method called by the others
    def add_log(self, message):
        self.lock.acquire()

        domain_fd = open(self.domain_filepath, "a")
        all_fd = open(self.all_filepath, "a")
        dt = datetime.now().strftime("%d:%m:%Y.%H:%M:%S:%f")

        domain_fd.write(dt + " " + message + "\n")
        all_fd.write(dt + " " + message + "\n")

        if self.is_debug == True:
            sys.stdout.write(dt + " " + message + "\n")

        domain_fd.close()
        all_fd.close()

        self.lock.release()



