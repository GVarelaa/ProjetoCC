# Author: Guilherme Varela
# Created at: 02/11/22
# Last update: 02/11/12
# Description:


class Query_Info:

    def __init__(self,
                 name,
                 type_of_value):
        self.__name = name
        self.__type_of_value = type_of_value


    def get_name(self):
        return self.__name

    def get_type_of_value(self):
        return self.__type_of_value