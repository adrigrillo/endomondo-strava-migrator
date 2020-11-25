from configparser import ConfigParser, NoOptionError

from loguru import logger
from stravalib import Client

from src.utils.parameters import ACCESS, TOKEN


def get_strava_client(config: ConfigParser) -> Client:
    """ Checks the authentication token and generates the Strava client.

    Args:
        config: app configuration where the token is saved.

    Returns:
        if exist, strava client configured with the authentication token.

    Raises:
        ValueError: If no token is found in the configuration.

    """
    try:
        token = config.get(ACCESS, TOKEN)
        if not token:
            logger.error('You should write your app token in the configuration.')
            raise ValueError('The token has not been set in the configuration.')
    except NoOptionError:
        raise ValueError('The token has not been set in the configuration.')
    
    client = Client()
    client.access_token = token

    return client