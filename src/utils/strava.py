# -*- coding: utf-8 -*-
"""
utils/strava.py
=================
Utility class to Strava API
"""
import json
import time
from configparser import ConfigParser, NoOptionError
from datetime import datetime
from pathlib import Path
from typing import Tuple

from loguru import logger
from stravalib import Client, exc

from utils.parameters import SECRET
from utils.constants import CONFIG_PATH, CODE_ID_FILE_NAME, TOKEN_FILE_NAME
from utils.files_handler import check_folder
from utils.parameters import STRAVA, CLIENT_ID


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


def get_strava_token_from_code_id(config: ConfigParser) -> str:
    """ Method that interchange the temporary authentication code obtained
    when `src/request_auth.py` is executed. The method reads the file
    `config/code_id.txt` that contains the temporal authentication and generates
    the POST request to obtain the final access token which is saved in
    `config/token.json`.

    This method requires the Strava application `client_id` and `secret` that
    has to be set in the configuration file (`config/config.ini`).

    Args:
        config (ConfigParser): app configuration.

    Returns:
        str: Strava access token.

    Raises:
        ValueError: If no token is found in the configuration.
    """
    code_id_path = Path(CONFIG_PATH, CODE_ID_FILE_NAME)
    if not code_id_path.is_file():
        raise ValueError('The file with the temporal authentication code (`config/code_id.txt`)'
                         'was NOT found. Execute `request_auth.py` to obtain the temporal access.')

    with open(code_id_path, 'r') as file:
        logger.debug('The file with the temporal authentication code (`config/code_id.txt`)'
                     'was found.')
        code_id = file.read()

    if not code_id:
        raise ValueError('No valid temporal code access found. Rerun `request_auth.py` '
                         'to obtain the temporal access.')

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


def get_strava_client(config: ConfigParser) -> Client:
    """ Checks the authentication token and generates the Strava client.

    Args:
        config (ConfigParser): app configuration.

    Returns:
        if exist, strava client configured with the authentication token.
    """
    token_file_path = Path(check_folder(CONFIG_PATH), TOKEN_FILE_NAME)
    if token_file_path.is_file():
        logger.debug('The token info file (`config/token.json`) was found.')
        with open(token_file_path, 'r') as file:
            token_data = json.load(file)

        token = token_data.get('access_token')
        # If the file exists but no access token found, check against the temporary auth
        if not token:
            logger.warning('The token info file (`config/token.json`) was found'
                           ' but the access token could not be read.')
            token = get_strava_token_from_code_id(config)

    else:
        logger.info('The token info file (`config/token.json`) was NOT found. '
                    'Retrieving from the temporal authentication code.')
        token = get_strava_token_from_code_id(config)

    client = Client(access_token=token)
    return client


def upload_activity(client: Client, activity_type: str, file_path: Path) -> bool:
    """ Helper method to upload the activity to Strava. This method will handle
    the different possibilities when uploading an activity.

    Args:
        client (Client): configured Strava client.
        activity_type (str): Strava activity string.
        file_path (Path): Path to the `*.tcx` activity file.

    Returns:
        bool: True if the activity have been uploaded successfully. False otherwise.

    Raises:
        RateLimitExceeded: When the API limits have been reached. Generally when
        more than 1000 petitions have been done during the day.
        ConnectionError: When it has been impossible to connect the Strava servers.
        Exception: Unknown exceptions that will be logged in detail.
    """
    try:
        activity_file = open(file_path, 'r')
        client.upload_activity(
            activity_file=activity_file,
            data_type='tcx',
            activity_type=activity_type,
            private=False
        )
    except exc.ActivityUploadFailed:
        logger.exception('Error uploading the activity `{}`.', file_path.stem)
        return False
    except exc.RateLimitExceeded:
        logger.exception('Exceeded the API rate limit.')
        raise
    except ConnectionError:
        logger.exception('No internet connection.')
        raise
    except Exception:
        logger.exception('Unknown exception')
        raise

    # If no error return true
    logger.debug('Activity `{}` uploaded sucessfully.', file_path.stem)
    return True


def handle_rate_limit(start_time: float, requests: int) -> Tuple[float, int]:
    """ Method to handle the 15 minutes API limit. This method will check the
    elapsed time since the first request and the number of them. Three cases
    are possible:

    - Less than 15 minutes elapsed from the first request and less than 100
      requests -> continue.
    - More than 15 minutes elapsed from the first request and less than 100
      requests -> reset timer and request number to count from 0 again.
    - Less than 15 minutes elapsed from the first request but more than 100
      requests -> sleep until the 15 minutes block is over and reset timer
      and request number to count from 0 again.

    Args:
        start_time (float): timestamp of the first request of the block.
        requests (int): number of request done in the block.

    Returns:
        float, int: updated start time and number of requests following the
                    possible cases.
    """
    requests += 1
    elapsed_time = time.time() - start_time
    if elapsed_time <= 60 * 15:
        if requests >= 100:
            remaining_time_stopped = 60 * 15 - elapsed_time
            mins, secs = divmod(remaining_time_stopped, 60)
            logger.warning('The number of allowed request per 15 minutes have'
                           'been reached. Sleeping for {:0.0f} minutes, {:0.1f} seconds.',
                           mins, secs)
            time.sleep(remaining_time_stopped)
            # Reset values. Include petition to be processed
            logger.info('Waiting time elapsed. Continuing with the process.')
            requests = 1
            start_time = time.time()

    else:
        logger.debug('15 minutes have been elapsed. Resetting requests and time.')
        # Reset values. Include petition to be processed
        requests = 1
        start_time = time.time()

    return start_time, requests
