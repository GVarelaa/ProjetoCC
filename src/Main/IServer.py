# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 30/10/12
# Description: Defines the interface for a server
# Last update: Added interpretQuery method

import zope.interface

class IServer(zope.interface.Interface):
    def interpretQuery(self, query):
        pass