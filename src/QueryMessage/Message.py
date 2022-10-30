# PDU of a query: Header, Data

from Header import Header
from Data import Data

class Message:
    def __init__(self, header, data):
        self.__header = header
        self.__data = data