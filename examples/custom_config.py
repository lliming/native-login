"""
Example for a custom config.

At some point, your client will probably need to have it's own config mechanism
for your app-specific config values. To use a custom config, all you need to
do is provide the read/write/clear hooks.
"""
from native_login import NativeClient, TokenStorage
from myconfig import config


class MyTokenStorage(TokenStorage):

    def write_tokens(self, tokens):
        config.save(tokens, section='tokens')

    def read_tokens(self):
        config.load(section='tokens')

    def clear_tokens(self):
        config.remove(section='tokens')


# Using your custom Token Handler:
app = NativeClient(client_id='',
                   token_handler=MyTokenStorage())

# Calls read() then write()
app.login()

# Calls read()
tokens = app.load_tokens()

# Calls clear()
app.revoke_tokens()
