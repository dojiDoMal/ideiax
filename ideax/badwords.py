import json


class Badword:
    blacklist = []

    def __init__(self, datafile=None):
        if datafile:
            self.blacklist = self.load_json(datafile)

    def __contains__(self, txt):
        return bool(set(self.blacklist) & set(txt.lower().split()))

    def __iter__(self):
        return iter(self.blacklist)

    def load_json(self, file):
        with open(file) as f:
            data = json.load(f)
        return [item.lower() for item in data]

    def search_badwords(self, txt):
        """Old method for compatibility, prefer to use `in` operator"""
        return txt in self
