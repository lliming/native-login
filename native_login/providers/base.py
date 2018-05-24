

class NativeAuthenticator:

    def __init__(self, config):
        self.app_name = config.get('app_name', '')
        self.client_id = config.get('client_id')
        self.scopes = config.get('scopes', [])
        self.refresh_tokens = config.get('refresh_tokens', False)

    def get_url(self):
        raise NotImplemented()

    def authenticate(self, auth_code):
        raise NotImplemented()