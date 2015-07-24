import json
import sys
import threading

class configmanager():
    def __init__(self):
        self.__lastConfigRead = ""
        self.filename = 'db.json'
        self.__lock = threading.Lock()

    def readConfig(self):
        try:
            data = open(self.filename).read()
            self.__lastConfigRead = json.loads(data)
            return self.__lastConfigRead
        except IOError as error:
            print error
            print "Unable to read stream config, terminating..."
            sys.exit(0)

    def isStreamExist(self, site, stream):
        if stream in self.__lastConfigRead[site]:
            return True
        else:
            return False

    def listSites(self):
        return self.__lastConfigRead.keys()

    def writeStream(self, site, stream):
        with self.__lock:
            self.__lastConfigRead[site].append(stream)
            with open(self.filename, 'w') as newFile:
                json.dump(self.__lastConfigRead, newFile, indent=4)
                return True
        return False

    def removeStream(self, site, stream):
        with self.__lock:
            self.__lastConfigRead[site].remove(stream)
            with open(self.filename, 'w') as newFile:
                json.dump(self.__lastConfigRead, newFile, indent=4)
                return True
        return False

    def getConfiguredStreamsFromSite(self, site):
        return self.__lastConfigRead[site]