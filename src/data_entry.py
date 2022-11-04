# Author: Gabriela Cunha, Guilherme Varela and Miguel Braga
# Created at: 30/10/22
# Last update date: 4/11/22
# Description: DataBase entries (value, expiration, priority)
# Last update: Changed class attributes to a more general entry

class DataEntry: 
    def __init__(self, value, ttl, priority):
        self.value = value
        self.ttl = ttl
        self.priority = priority

    def __str__(self):
        return str(self.value) + " " + str (self.ttl) + " " + str(self.priority)

    def __repr__(self):
        return str(self.value) + " " + str(self.ttl) + " " + str(self.priority)
