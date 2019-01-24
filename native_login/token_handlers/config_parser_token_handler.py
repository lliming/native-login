import os
from six.moves.configparser import ConfigParser

from native_login.token_handlers.base import TokenHandler


class ConfigParserTokenHandler(TokenHandler):

    CONFIG_TOKEN_GROUPS = "token_groups"
    CFG_SECTION = 'tokens'

    def write(self, tokens):
        config = ConfigParser()
        config.add_section(self.CFG_SECTION)
        for name, value in tokens.items():
            config.set(self.CFG_SECTION, name, value)
        with open(self.filename, 'w') as configfile:
            config.write(configfile)

    def read(self):
        config = ConfigParser()
        config.read(self.filename)
        return dict(config.items(self.CFG_SECTION))

    def clear(self):
        os.remove(self.filename)

    def serialize(self, oauth_token_response):
        """
        Take a dict of tokens organized by resource server and return a dict
        that can be easily saved to the config file.
        Resource servers containing '.' in their name will automatically be
        converted to '_' (auth.globus.org == auth_globus_org). This is only for
        cosmetic reasons. A resource server named "foo=;# = !@#$%^&*()" will
        have funky looking config keys, but saving/loading will behave
        normally. Int values are converted to string, None values are converted
        to empty string. *No other types are checked*.
        `tokens` should be formatted:
        {
            "auth.globus.org": {
                "scope": "profile openid email",
                "access_token": "<token>",
                "refresh_token": None,
                "token_type": "Bearer",
                "expires_at_seconds": 1539984535,
                "resource_server": "auth.globus.org"
            }, ...
        }
        Returns a flat dict of tokens prefixed by resource server.
        {
            "auth_globus_org_scope": "profile openid email",
            "auth_globus_org_access_token": "<token>",
            "auth_globus_org_refresh_token": "",
            "auth_globus_org_token_type": "Bearer",
            "auth_globus_org_expires_at_seconds": "1540051101",
            "auth_globus_org_resource_server": "auth.globus.org",
            "token_groups": "auth_globus_org"
        }"""
        tokens = oauth_token_response.by_resource_server
        serialized_items = {}
        token_groups = []
        for token_set in tokens.values():
            token_groups.append(self.serialize_token(
                token_set["resource_server"]))
            for key, value in token_set.items():
                key_name = self.serialize_token(token_set["resource_server"],
                                                key)
                if isinstance(value, int):
                    value = str(value)
                if value is None:
                    value = ""
                serialized_items[key_name] = value

        serialized_items[self.CONFIG_TOKEN_GROUPS] = ",".join(token_groups)
        return serialized_items

    def deserialize(self, config_items):
        """
        Takes a dict from a config section and returns a dict of tokens by
        resource server. `config_items` is a raw dict of config options
        returned from get_parser().get_section().
        Returns tokens in the format:
        {
            "auth.globus.org": {
                "scope": "profile openid email",
                "access_token": "<token>",
                "refresh_token": None,
                "token_type": "Bearer",
                "expires_at_seconds": 1539984535,
                "resource_server": "auth.globus.org"
            }, ...
        }
        """
        token_groups = {}

        tsets = config_items.get(self.CONFIG_TOKEN_GROUPS)
        config_token_groups = tsets.split(',')
        for group in config_token_groups:
            tset = {k: config_items.get(self.deserialize_token(group, k))
                    for k in self.TOKEN_KEYS}
            tset['expires_at_seconds'] = int(tset['expires_at_seconds'])
            # Config loaded 'null' values will be an empty string. Set these to
            # None for consistency
            tset = {k: v if v else None for k, v in tset.items()}
            token_groups[tset['resource_server']] = tset

        return token_groups

    def deserialize_token(self, grouping, token):
        return '{}{}'.format(grouping, token)

    def serialize_token(self, resource_server, token=''):
        return '{}_{}'.format(resource_server.replace('.', '_'), token)
