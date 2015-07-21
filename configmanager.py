import json
import sys

class configmanager():
    def __init__(self):
        self.lastConfigRead = ""
        self.filename = 'db.json'

    def readConfig(self):
        try:
            data = open(self.filename).read()
            return json.loads(data)
        except IOError as error:
            print error
            print "Unable to read stream config, terminating..."
            sys.exit(0)

    def writeStream(self, site, stream):
        return