# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 30/10/12
# Description: Header of a DNS Message

from enum import Enum

class Header:
    def __init__(self, # For now, all attributes are strings
                 msg_id, 
                 flags, 
                 response_code, 
                 num_values, 
                 num_authorities, 
                 num_extra_values):
        self.msg_id = msg_id
        self.flags = flags
        self.response_code = response_code
        self.num_values = num_values
        self.num_authorities = num_authorities
        self.num_extra_values = num_extra_values

    def __str__(self):
        return self.msg_id + " | " + self.flags + " | " + self.response_code + " | " + self.num_values + " | " + self.num_authorities + " | " + self.num_extra_values

    def __repr__(self):
        return self.msg_id + " | " + self.flags + " | " + self.response_code + " | " + self.num_values + " | " + self.num_authorities + " | " + self.num_extra_values

