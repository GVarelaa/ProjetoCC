# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 30/10/12
# Description: PDU of a query: Header, Data

from header import Header
from data import Data

class Message:
    def __init__(self, header, data):
        self.__header = header
        self.__data = data