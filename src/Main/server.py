# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 02/11/12
# Description: Implements a server, a Primary Server
# Last update: Added basic structure

from src.IO.parser import parser_df
from src.IO.parser import parser_st
from src.IO.parser import parser_cf

class Server:
    def __init__(self, config_file_path):
        (d, d_fp, ps, ss, dd, rfp, lfp) = parser_cf(config_file_path)
        self.domain = d
        self.data_file_path = d_fp
        self.primary_server = ps    # caso de o servidor ser secundário
        self.secondary_servers = ss # caso de o servidor ser primário
        self.default_domains = dd
        self.root_servers_file_path = rfp
        self.log_file_path = lfp

        self.server_type = None   # if

        self.root_servers = parser_st(rfp)
        self.db = parser_df(d_fp)

    def __str__(self):
        return f"Domínio: {self.domain}\nBase de Dados Diretoria: {self.data_file_path}\nBase de Dados: {self.db}\nServidore primário: {self.primary_server}\nServidores secundários: {self.secondary_servers}\nDomínios por defeito: {self.default_domains}\nRoot Servers: {self.root_servers}\nFicheiro de Log: {self.log_file_path}"
    
    def __repr__(self):
        return f"Domínio: {self.domain}\nBase de Dados Diretoria: {self.data_file_path}\nBase de Dados: {self.db}\nServidore primário: {self.primary_server}\nServidores secundários: {self.secondary_servers}\nDomínios por defeito: {self.default_domains}\nRoot Servers: {self.root_servers}\nFicheiro de Log: {self.log_file_path}"


    def response_query(self, query): #objeto do tipo message
        header = query.header
        data = query.data
        flag = header.flags

        if 'Q' in flag:
            name = data.query_info.name
            type_of_value = data.query_info.type_of_value

            db_data = self.db[name, type_of_value]
            authorities_values = self.db[name, "NS"]

            if len(db_data) == 0:
                return None
            else:
                header.flags = "A"
                header.responde_code = "0" # alterar
                header.num_values = str(len(db_data))
                header.num_authorities = len(authorities_values)
                header.num_extra_values = None

                data.response_values = db_data
                data.authorities_values = authorities_values
                data.extra_values = None

            #header_response = Header(message_id, "A", response_code, num_values, )


p = Server("config.txt")
print(p)