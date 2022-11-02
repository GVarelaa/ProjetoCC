# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 30/10/12
# Description:


class Query_Data:
    def __init__(self,
                 query_info,
                 response_values,
                 authorities_values,
                 extra_values):
        self.__query_info = query_info
        self.__responde_values = response_values
        self.__authorities_values = authorities_values
        self.__extra_values = extra_values

    def get_query_info(self):
        return self.__query_info

    def get_response_values(self):
        return self.__responde_values

    def get_authorities_values(self):
        return self.__authorities_values

    def get_extra_values(self):
        return self.__extra_values

