# Author: Guilherme Varela
# Created at: 30/10/22
# Last update: 03/11/12
# Description: Implements a server, a Primary Server
# Last update: Added basic structure

from parser import parser_df
from parser import parser_st
from parser import parser_cf
from query_message.message import *
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
        return f"Domínio: {self.domain}\nBase de Dados Diretoria: {self.data_file_path}\nBase de Dados: {self.db}\nServidor primário: {self.primary_server}\nServidores secundários: {self.secondary_servers}\nDomínios por defeito: {self.default_domains}\nRoot Servers: {self.root_servers}\nFicheiro de Log: {self.log_file_path}"
    
    def __repr__(self):
        return f"Domínio: {self.domain}\nBase de Dados Diretoria: {self.data_file_path}\nBase de Dados: {self.db}\nServidor primário: {self.primary_server}\nServidores secundários: {self.secondary_servers}\nDomínios por defeito: {self.default_domains}\nRoot Servers: {self.root_servers}\nFicheiro de Log: {self.log_file_path}"


    def response_query(self, query): #objeto do tipo message
        (message_id, flags, name, type_of_value) = parse_message(query)

        response = ""

        if 'Q' in flags:
            response_values = self.db[name, type_of_value]
            authorities_values = self.db[name, "NS"]
            extra_values = list()

            for (p, tv) in self.db.keys(): # meter isto numa função
                print(p)
                if tv == "A":
                    for (value, ttl, expiration) in response_values:
                        if p == value:
                            for (v1, e1, p1) in self.db[p,tv]:
                                extra_values.append((p,tv) + (v1,e1,p1))

                    for (value, ttl, expiration) in authorities_values:
                        if p == value:
                            for (v1, e1, p1) in self.db[p, tv]:
                                extra_values.append((p, tv) + (v1, e1, p1))

            if len(response_values) == 0:
                return None # alterar
            else:
                response = build_query_response(query, response_values, authorities_values, extra_values)

            return response


p = Server("files/config.txt")
print(p.db)
#print(p.response_query("3874,Q+R,0,0,0,0;example.com.,MX;"))


