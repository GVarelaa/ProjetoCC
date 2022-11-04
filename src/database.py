# Authors: Gabriela Cunha, Guilherme Varela and Miguel Braga
# Created at: 30/10/22
# Last update date: 4/11/22
# Description: Module that implements a database for storing data records (ex: A, NS, CNAME, etc)
# Last update: Changed data structure to dictionary of dictionaries and implemented the methods of put, get

from data_entry import DataEntry


class Database:
    def __init__(self, dict={}):
        self.dict = dict

    def __str__(self):
        return str(self.dict)

    def __repr__(self):
        return str(self.dict)

    # Entry (type, parameter, value, expiration, priority)
    def add_entry(self, entry, entry_type, entry_parameter):
        if entry_type not in self.dict:
            self.dict[entry_type] = {}

        if entry_parameter not in self.dict[entry_type].keys():
            self.dict[entry_type][entry_parameter] = list()

        self.dict[entry_type][entry_parameter].append(entry)

    # Gets all entries with the given entry_type
    # Example: All entries with type 'A' -- Addresses
    def get_values_by_type(self, entry_type):
        entries = []
        if entry_type in self.dict.keys():
            of_type = self.dict[entry_type]

            if of_type is not None:
                for key in of_type.keys():
                    for entry in of_type[key]:
                        entries.append(entry)

        return entries

    def get_values_by_type_and_parameter(self, entry_type, entry_parameter):
        if entry_type in self.dict.keys():
            if entry_parameter in self.dict[entry_type].keys():
                return self.dict[entry_type][entry_parameter]


    def get_type_keys(self):
        return self.dict.keys()

    def get_parameter_keys(self, type):
        return self.dict[type].keys()

    def get_value(self, key):
        return None

    def update_value(self, key):
        return None