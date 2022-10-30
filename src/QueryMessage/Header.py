# Header of a DNS Message

from enum import Enum

class DnsFlag(Enum):
    Q = 1
    R = 2
    A = 3

class Header:
    def __init__(self, # For now, all attributes are strings
                 msg_id, 
                 flags, 
                 response_code, 
                 num_values, 
                 num_authorities, 
                 num_extra_values):
        self.__msg_id = msg_id
        self.__flags = flags
        self.__response_code = response_code
        self.__num_values = num_values
        self.__num_authorities = num_authorities
        self.__num_extra_values = num_extra_values

    def __str__(self):
        return self.__msg_id + " | " + self.__flags + " | " + self.__response_code + " | " + self.__num_values + " | " + self.__num_authorities + " | " + self.__num_extra_values

    def __repr__(self):
        return self.__msg_id + " | " + self.__flags + " | " + self.__response_code + " | " + self.__num_values + " | " + self.__num_authorities + " | " + self.__num_extra_values
    