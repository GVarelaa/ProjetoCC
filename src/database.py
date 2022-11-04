# Author: Miguel Braga
# Created at: 30/10/22
# Last update date: 4/11/22
# Description: Module that implements a database for storing data records (ex: A, NS, CNAME, etc)
# Last update: Changed data structure to dictionary of dictionaries and implemented the methods of put, get

from data_entry import DataEntry


class Database:
    def __init__(self, dic={}):
        self.dic = dic

    def __str__(self):
        return str(map)

    def __repr__(self):
        return str(map)

    # Entry (type, parameter, value, expiration, priority)
    def add_entry(self, entry):
        if entry.type not in self.dic:
            self.dic[entry.type] = {}

        if entry.parameter not in self.dic[entry.type].keys():
            self.dic[entry.type][entry.parameter] = list()

        self.dic[entry.type][entry.parameter].append(entry)

    # Gets all entries with the given entry_type
    # Example: All entries with type 'A' -- Addresses
    def get_values_by_entry_type(self, entry_type):
        entries = []
        if type in self.dic.keys():
            ofType = self.dic[type]

            if ofType is not None:
                for key in ofType.keys():
                    for entry in ofType[key]:
                        entries.append(entry)

        return entries

    def get_values_by_entry_type_and_parameter(self, entry_type, entry_parameter):
        if entry_type in self.dic.keys():
            if entry_parameter in self.dic[entry_type].keys():
                return self.dic[entry_type][entry_parameter]


    def getValue(self, key):
        return None

    def updateValue(self, key):
        return None


c = Cache({})
e = DataEntry("A", "ns1", "193.136.130.250", "86400", "0")
e2 = DataEntry("A", "ns2", "193.136.130.251", "86400", "0")
e3 = DataEntry("NS", "example.com", "ns1.example.com.", "86400", "0")
e4 = DataEntry("NS", "example.com", "ns2.example.com.", "86400", "0")
c.add_entry(e)
c.add_entry(e2)
c.add_entry(e3)
c.add_entry(e4)
print(c.get_values_by_entry_type_and_parameter("NS", "example.com"))
