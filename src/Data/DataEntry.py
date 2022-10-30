# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 30/10/12

# Description: Dados do tipo <end_ip> <ttl> <priority>

class DataEntry: 
    def __init__(self, ip_add, ttl, priority):
        self.__ip_add = ip_add
        self.__ttl = ttl 
        self.__priority = priority

    def set_ip_add(self, new_ip_add):
        self.__ip_add = new_ip_add

    def get_ip_add(self):
        return self.__ip_add

    def set_ttl(self, new_ttl):
        self.__ttl = new_ttl

    def get_ttl(self):
        return self.__ttl

    def set_priority(self, new_priority):
        self.__priority = new_priority

    def get_priority(self):
        return self.__priority

d = DataEntry("192.168.1.2", 4, 1)
print(d.__ip_add)