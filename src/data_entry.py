# Author: Miguel Braga
# Created at: 30/10/22
# Last update date: 4/11/22
# Description: DataBase entries (type, parameter, value, expiration, priority)
# Last update: Changed class attributes to a more general entry

class DataEntry: 
    def __init__(self, entry_type, parameter, value, expiration, priority):
        self.type = entry_type
        self.parameter = parameter
        self.value = value
        self.expiration = expiration
        self.priority = priority

    def __str__(self):
        return str(self.parameter) + " " \
               + str(self.type) + " " \
               + str(self.value) + " " \
               + str (self.expiration) + " " \
               + str(self.priority)

    def __repr__(self):
        return str(self.parameter) + " " \
               + str(self.type) + " " \
               + str(self.value) + " " \
               + str(self.expiration) + " " \
               + str(self.priority)
