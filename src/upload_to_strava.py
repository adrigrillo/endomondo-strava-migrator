# -*- coding: utf-8 -*-
"""
upload_to_strava.py
=================
Main class of the application. This file is the one executed to upload the
endomondo activities to strava from the export folder.
"""
from pathlib import Path

import fire
from loguru import logger
from stravalib.exc import ActivityUploadFailed, TimeoutExceeded
from tqdm import tqdm

from parsers.endomondo import retrieve_json_data, get_activity_type
from src.utils.config_handler import init_app
from src.utils.strava import get_strava_client
from transform.endomondo_strava import transform_activity
from utils.files_handler import get_activity_files_names, retrieve_activities_path
from utils.parameters import SYSTEM, PATH


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

    processed_activities = list()
    for activity in tqdm(activity_files):
        logger.debug('Processing workout file `{}`', activity)
        # Load json first to obtain the data that will be sent along the tcx
        activity_data = retrieve_json_data(activities_folder, activity)
        endomondo_activity_type = get_activity_type(activity_data)
        strava_activity_type = transform_activity(endomondo_activity_type)

        tcx_file_path = Path(activities_folder, f'{activity}.tcx')
        try:
            activity_file = open(tcx_file_path, 'r')
            activity_upload = client.upload_activity(
                activity_file=activity_file,
                data_type='tcx',
                activity_type=strava_activity_type,
                private=False
            )
        except ActivityUploadFailed:
            logger.exception('Error uploading the activity.')
            continue
        except ConnectionError:
            logger.exception('No internet connection.')
            continue

        processed_activities.append(activity)

        processed_activities_file_path = Path(app_config.get(SYSTEM, PATH), 'processed.txt')
    with open(processed_activities_file_path, 'w') as file:
        file.writelines(processed_activities)


if __name__ == '__main__':
    fire.Fire(upload)
