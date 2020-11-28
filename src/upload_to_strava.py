# -*- coding: utf-8 -*-
"""
upload_to_strava.py
=================
Main class of the application. This file is the one executed to upload the
endomondo activities to strava from the export folder.
"""
import shutil
from pathlib import Path
from time import mktime, strptime

import fire
from loguru import logger
from stravalib.exc import ActivityUploadFailed, RateLimitExceeded
from tqdm import tqdm

from parsers.endomondo import retrieve_json_data, get_activity_type
from src.utils.config_handler import init_app
from src.utils.strava import get_strava_client
from transform.endomondo_strava import transform_activity
from utils.constants import CONFIG_PATH
from utils.files_handler import get_activity_files_names, retrieve_activities_path, check_folder


def upload(path: str = None,
           config: str = '../config/config.ini'):
    """

    Args:
        path: path to the folder containing the activities.
        config: path to the configuration file.

    Returns:

    """
    app_config = init_app(config)
    client = get_strava_client(app_config)

    activities_folder = retrieve_activities_path(path, app_config)
    activity_files = get_activity_files_names(activities_folder)

    # Create processed and error folder in activities path
    processed_path = check_folder(Path(activities_folder, 'processed'))
    error_path = check_folder(Path(activities_folder, 'error'))

    # Control processed activities to avoid repetition
    processed_activities_file_path = Path(CONFIG_PATH, 'last_processed.txt')
    if processed_activities_file_path.is_file():
        processed_file = open(processed_activities_file_path, 'r')
        last_processed = processed_file.read()
    else:
        last_processed = None

    # LOOOOOOOOP
    for activity in tqdm(activity_files):
        # Check if the activity has been previously processed
        if last_processed:
            logger.debug('Checking activity `{}` against last processed `{}`.', activity, last_processed)
            comp_last = mktime(strptime(last_processed, "%Y-%m-%d %H:%M:%S.%f"))
            comp_now = mktime(strptime(activity, "%Y-%m-%d %H:%M:%S.%f"))
            if comp_last <= comp_now:
                logger.info('Activity {} was already processed. Skipping', activity)
                continue
            # We are processing older workouts, so it is not necessary to check everytime
            else:
                logger.debug('Processing older workouts.')
                last_processed = None

        logger.debug('Processing workout file `{}`', activity)
        # Load json first to obtain the data that will be sent along the tcx
        activity_data = retrieve_json_data(activities_folder, activity)
        endomondo_activity_type = get_activity_type(activity_data)
        strava_activity_type = transform_activity(endomondo_activity_type)

        tcx_file_path = Path(activities_folder, f'{activity}.tcx')
        try:
            activity_file = open(tcx_file_path, 'r')
            client.upload_activity(
                activity_file=activity_file,
                data_type='tcx',
                activity_type=strava_activity_type,
                private=False
            )
        except ActivityUploadFailed:
            logger.exception('Error uploading the activity.')
            # Copy the file to the processed path
            shutil.move(tcx_file_path,
                        Path(error_path, f'{activity}.tcx'))
            shutil.move(Path(activities_folder, f'{activity}.json'),
                        Path(error_path, f'{activity}.json'))
            continue
        except RateLimitExceeded:
            logger.exception('Exceeded the API rate limit.')
            raise
        except ConnectionError:
            logger.exception('No internet connection.')
            continue
        except Exception as error:
            logger.exception('Unknown exception')
            raise error

        # Save last processed in case of interruption
        with open(processed_activities_file_path, 'w') as file:
            logger.trace('Writing last processed activity `{}`.', activity)
            file.write(activity)

        # Copy the file to the processed path
        shutil.move(tcx_file_path,
                    Path(processed_path, f'{activity}.tcx'))
        shutil.move(Path(activities_folder, f'{activity}.json'),
                    Path(processed_path, f'{activity}.json'))





if __name__ == '__main__':
    fire.Fire(upload)
