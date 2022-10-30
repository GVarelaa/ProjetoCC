from datetime import datetime

class Log:
    def __init__(self, filepath):
        self.filepath = filepath
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





    def add_log(self, message):
        dt = datetime.now().strftime("%d:%m:%Y.%H:%M:%S:%f")

        self.fd.write(dt + " " + message + "\n")



l = Log("teste.txt")
l.log_qe("192.168.0.0", "nao sei")
