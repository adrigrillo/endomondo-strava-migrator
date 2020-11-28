# -*- coding: utf-8 -*-
"""
utils/strava.py
=================
Utility class to Strava API
"""
import json
from configparser import ConfigParser, NoOptionError
from datetime import datetime
from pathlib import Path

from loguru import logger
from stravalib import Client

from src.utils.parameters import TOKEN, SECRET
from utils.constants import CONFIG_PATH, CODE_ID_FILE_NAME, TOKEN_FILE_NAME
from utils.files_handler import check_folder
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
    token_file_path = Path(check_folder(CONFIG_PATH), TOKEN_FILE_NAME)
    if token_file_path.is_file():
        with open(token_file_path, 'r') as file:
            token_data = json.load(file)

        token = token_data.get('access_token')
        # If the file exists but no access token found, check against the temporary auth
        if not token:
            logger.warning('The token data was found but the access token could'
                           'not be read.')
            token = get_strava_token_from_code_id(config)

    else:
        token = get_strava_token_from_code_id(config)

    client = Client(access_token=token)
    return client


def get_strava_token_from_code_id(config: ConfigParser) -> str:
    logger.info('No token was defined in the configuration file. Retrieving from'
                'the temporal authentication code.')

    code_id_path = Path(CONFIG_PATH, CODE_ID_FILE_NAME)
    if not code_id_path.is_file():
        logger.error('No temporal authentication code found. Execute '
                     '`request_auth.py` to obtain the temporal access.')
        raise ValueError('No access token found.')

    with open(code_id_path, 'r') as file:
        code_id = file.read()

    if not code_id:
        raise ValueError('No valid temporal code access found. Rerun '
                         '`request_auth.py` to obtain the temporal access.')

    client = Client()
    token = client.exchange_code_for_token(client_id=get_client_id(config),
                                           client_secret=get_secret(config),
                                           code=code_id)

    logger.debug('Obtained access until {}:\n'
                 '- token: {}.'
                 '- refresh token: {}.',
                 datetime.utcfromtimestamp(int(token['expires_at'])).strftime('%d-%m-%Y %H:%M:%S'),
                 token['access_token'], token['refresh_token'])

    # Save JSON with the response
    save_path = Path(check_folder(CONFIG_PATH), TOKEN_FILE_NAME)
    with open(save_path, 'w') as file:
        logger.info('Writing token information to `{}`.', save_path)
        json.dump(token, file, indent=4)

    return token['access_token']


def get_client_id(app_config: ConfigParser) -> int:
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


def get_secret(app_config: ConfigParser) -> str:
    """ Obtains the secret from the configuration file.

    Args:
        app_config (ConfigParser): app configuration.

    Returns:
        str: secret from the configuration file.

    Raises:
        NoOptionError: If the `secret` key is not
         present in the configuration.
    """
    try:
        secret = app_config.get(STRAVA, SECRET)
    except NoOptionError:
        raise ValueError('The client id has not been set in the configuration.')

    return secret
