import json
import os
from native_login.token_storage.base import TokenStorage


class JSONTokenStorage(TokenStorage):

    def write(self, tokens):
        with open(self.filename, 'w+') as fh:
            json.dump(tokens, fh, indent=2)

    def read(self):
        if not os.path.exists(self.filename):
            return None
        with open(self.filename) as fh:
            return json.load(fh)

    def clear(self):
        os.remove(self.filename)
