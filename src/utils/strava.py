# -*- coding: utf-8 -*-
"""
utils/strava.py
=================
Utility class to Strava API
"""
from configparser import ConfigParser, NoOptionError

from loguru import logger
from stravalib import Client

from src.utils.parameters import STRAVA, TOKEN
from utils.parameters import STRAVA, CLIENT_ID


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
        token = config.get(STRAVA, TOKEN)
        if not token:
            logger.error('You should write your app token in the configuration.')
            raise ValueError('The token has not been set in the configuration.')
    except NoOptionError:
        raise ValueError('The token has not been set in the configuration.')

    client = Client()
    client.access_token = token

    return client


def get_client_id(app_config: ConfigParser):
    """ Obtains the client ID from the configuration file.

    Args:
        app_config (ConfigParser): app configuration.

    Returns:
        int: client id from the configuration file.

    Raises:
        NoOptionError: If the `client_id` key is not
         present in the configuration.
        ValueError: If the client id is not an integer.
    """
    try:
        client_id = app_config.getint(STRAVA, CLIENT_ID)
    except NoOptionError:
        raise ValueError('The client id has not been set in the configuration.')
    except ValueError:
        logger.exception('Invalid client id format.')
        raise

    return client_id