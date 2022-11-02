# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 30/10/12

# Description: Dados do tipo <end_ip> <ttl> <priority>

class DataEntry: 
    def __init__(self, ip_add, ttl, priority):
        self.ip_add = ip_add
        self.ttl = ttl
        self.priority = priority



d = DataEntry("192.168.1.2", 4, 1)
print(d.ip_add)