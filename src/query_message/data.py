# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 30/10/12
# Description:

class QueryData:
    def __init__(self,
                 query_info,
                 response_values,
                 authorities_values,
                 extra_values):
        self.query_info = query_info
        self.response_values = response_values
        self.authorities_values = authorities_values
        self.extra_values = extra_values


