# Author: Gabriela Cunha, Guilherme Varela and Miguel Braga
# Created at: 30/10/22
# Last update date: 4/11/22
# Description: DataBase entries (value, expiration, priority)
# Last update: Changed class attributes to a more general entry

from enum import Enum
class Origin(Enum):
    FILE = 1
    SP = 2
    OTHERS = 3

class Status(Enum):
    FREE = 1
    VALID = 2

class ResourceRecord:
    def __init__(self, parameter, value_type, value, ttl, priority):
        self.parameter = parameter
        self.value_type = value_type
        self.value = value
        self.ttl = ttl
        self.priority = priority
        #self.origin = origin
        #self.time_stamp = time_stamp
        #self.index = index
        #self.status = status

    def __str__(self):
        return self.parameter + " " + self.value_type + " " + self.value + " " + str (self.ttl) + " " + str(self.priority)
                #+ " " + str(self.origin) + " " + str(self.time_stamp) + " " + str(self.index) + " " + str(self.status)

    def __repr__(self):
        return self.parameter + " " + self.value_type + " " + self.value + " " + str(self.ttl) + " " + str(self.priority)
               #+ " " + str(self.origin) + " " + str(self.time_stamp) + " " + str(self.index) + " " + str(self.status)
