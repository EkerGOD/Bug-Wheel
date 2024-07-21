import json
from base import System


class File:
    def __init__(self, path):
        self.path = path
        self.data = None

    def get(self):
        return self.data


class HistoryController(File, System):
    def __init__(self, path):
        super().__init__(path)
        with open(self.path, 'r') as file:
            self.data = json.load(file)

    def save(self):
        with open(self.path, 'w') as file:
            json_data = json.dumps(self.data, indent=4)
            file.write(json_data)

    def update(self, uid: int, items: dict):
        for key, value in items.items():
            self.data[str(uid)][key] = value

    def add(self, uid: int):
        self.data[str(uid)] = self.data['template']


class SiteController(File, System):
    def __init__(self, path):
        super().__init__(path)
        with open(self.path, 'r') as file:
            self.data = json.load(file)
