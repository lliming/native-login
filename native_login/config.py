import os
from configobj import ConfigObj

GENERAL_CONF = 'native_login'
DEFAULT_CONFIG = {
    GENERAL_CONF: {
        'provider': None
    }
}


def get_config_obj(file_error=False):
    path = os.path.expanduser("~/.native-login.cfg")

    return ConfigObj(path, encoding='utf-8', file_error=file_error)


def lookup_option(option, provider=None):
    conf = get_config_obj()
    try:
        if provider:
            return conf[provider][option]
        else:
            return conf[GENERAL_CONF][option]
    except KeyError:
        return None


def write_option(option, value, provider=None):
    """
    Write an option to disk -- doesn't handle config reloading
    """
    # deny rwx to Group and World -- don't bother storing the returned old mask
    # value, since we'll never restore it in the CLI anyway
    # do this on every call to ensure that we're always consistent about it
    os.umask(0o077)

    conf = get_config_obj()

    if provider:
        # add the section if absent
        if provider not in conf:
            conf[provider] = {}

        conf[provider][option] = value
    else:
        conf[GENERAL_CONF][option] = value
    conf.write()


def remove_option(option):
    conf = get_config_obj()

    # if there's no section for the option we're removing, just return None
    try:
        section = conf[GENERAL_CONF]
    except KeyError:
        return None

    try:
        opt_val = section[option]

        # remove value and flush to disk
        del section[option]
        conf.write()
    except KeyError:
        opt_val = None

    # return the just-deleted value
    return opt_val