import globus_sdk

from native_login.providers.base import NativeAuthenticator


class GlobusAuthenticator(NativeAuthenticator):
    GLOBUS_REDIRECT_URI = 'https://auth.globus.org/v2/web/auth-code'

    def get_url(self):
        client = globus_sdk.NativeAppAuthClient(client_id=self.client_id)
        # pass refresh_tokens=True to request refresh tokens
        client.oauth2_start_flow(
            requested_scopes=self.scopes,
            redirect_uri=self.GLOBUS_REDIRECT_URI,
            refresh_tokens=self.refresh_tokens)

        return client.oauth2_get_authorize_url()

    def authenticate(self, auth_code):
        client = globus_sdk.NativeAppAuthClient(client_id=self.client_id)
        token_response = client.oauth2_exchange_code_for_tokens(auth_code)
        tokens = token_response.by_resource_server
        access_token = tokens['auth.globus.org']['access_token']
        atclient = globus_sdk.AuthClient(
            authorizer=globus_sdk.AccessTokenAuthorizer(access_token))
        info = atclient.oauth2_userinfo()
        user_info = {
            'tokens': tokens,
            'name': info['name'],
            'email': info['email'],
            'sub': info['sub']
        }
        return user_info




def login():
    lookup_option('client_id', provider='globus')
    lookup_option()


def do_native_app_authentication(client_id, redirect_uri,
                                 requested_scopes=None):
    """
    Does a Native App authentication flow and returns a
    dict of tokens keyed by service name.
    """
    client = globus_sdk.NativeAppAuthClient(client_id=client_id)
    # pass refresh_tokens=True to request refresh tokens
    client.oauth2_start_flow(
        requested_scopes=requested_scopes,
        redirect_uri=redirect_uri,
        refresh_tokens=True)

    url = client.oauth2_get_authorize_url()

    print('Native App Authorization URL: \n{}'.format(url))

    if not is_remote_session():
        # There was a bug in webbrowser recently that this fixes:
        # https://bugs.python.org/issue30392
        if sys.platform == 'darwin':
            webbrowser.get('safari').open(url, new=1)
        else:
            webbrowser.open(url, new=1)

    auth_code = get_input('Enter the auth code: ').strip()

    token_response = client.oauth2_exchange_code_for_tokens(auth_code)
    tokens = token_response.by_resource_server
    access_token = tokens['auth.globus.org']['access_token']
    atclient = globus_sdk.AuthClient(
        authorizer=globus_sdk.AccessTokenAuthorizer(access_token))
    info = atclient.oauth2_userinfo()
    user_info = {
        'tokens': tokens,
        'name': info['name'],
        'email': info['email'],
        'sub': info['sub']
    }
    return user_info

def is_remote_session():
    """
    Check if this is a remote session, in which case we can't open a browser
    on the users computer. This is required for Native App Authentication (but
    not a Client Credentials Grant).
    Returns True on remote session, False otherwise.
    """
    return os.environ.get('SSH_TTY', os.environ.get('SSH_CONNECTION'))