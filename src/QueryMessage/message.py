# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 30/10/12
# Description: PDU of a query: Header, Data

from src.QueryMessage.header import Header
from src.QueryMessage.data import Query_Data

def build_message(name, type_of_value, flag):
    if flag == None:
        flag = "Q+R"
    else:
        flag = "Q"

    message = "1," + flag + ",0,0,0,0;" + name + "," + type_of_value + ";"
    print(message)

    return message


class Message:
    def __init__(self, header, data):
        self.header = header
        self.data = data