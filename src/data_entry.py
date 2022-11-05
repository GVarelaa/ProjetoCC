# Author: Gabriela Cunha, Guilherme Varela and Miguel Braga
# Created at: 30/10/22
# Last update date: 4/11/22
# Description: DataBase entries (value, expiration, priority)
# Last update: Changed class attributes to a more general entry

class DataEntry: 
    def __init__(self, parameter, value_type, value, ttl, priority):
        self.parameter = parameter
        self.value_type = value_type
        self.value = value
        self.ttl = ttl
        self.priority = priority

    def __str__(self):
        return self.parameter + " " + self.value_type + " " + self.value + " " + str (self.ttl) + " " + str(self.priority)

    def __repr__(self):
        return self.parameter + " " + self.value_type + " " + self.value + " " + str (self.ttl) + " " + str(self.priority)
