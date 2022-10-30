# Author: Miguel Braga
# Created at: 30/10/22
# Last update: 30/10/12
# Description: 

class Cache:
    def __init__(self, map = {}):
        self.map = map          # Vamos utilizar mesmo um map?
    
    def __str__(self):
        string = ""
        i = 1
        for key in self.map.keys():
            string += "Entrada número " + str(i) + ": " + str(key) + " -> " + str(self.map[key])
            i+=1

        return string

    def __repr__(self):
        return str(map)

    def addEntry(self, key, value):
        self.map[key] = value

    def getValue(self, key):
        return None

    def updateValue(self, key):
        return None
     

c = Cache({})
c.addEntry("123.134.154.21", "google.com")
print(str(c))