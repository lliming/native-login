

class LoginException(Exception):
    def __init__(self, code='', message=''):
        """
        :param code: A short string that can be checked against, such as
            'PermissionDenied'
        :param message: A longer string that describes the problem and action
            that should be taken.
        """
        self.code = code or 'UnexpectedError'
        self.message = message or 'Encountered an unknown login error'

    def __str__(self):
        return '{}: {}'.format(self.code, self.message)

    def __repr__(self):
        return str(self)

