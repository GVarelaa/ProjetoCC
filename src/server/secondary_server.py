import random
from server import server
from queries.axfr import *


class SecondaryServer(server.Server):
    def __init__(self, domain, default_domains, root_servers, log_path, primary_server):
        super().__init__(domain, default_domains, root_servers, log_path)
        self.primary_server = primary_server

    def __str__(self):
        return super().__str__() + \
               f"Server primário: {self.primary_server}\n"

    def __repr__(self):
        return super().__str__() + \
               f"Server primário: {self.primary_server}\n"



