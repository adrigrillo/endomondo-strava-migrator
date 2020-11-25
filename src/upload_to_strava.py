# -*- coding: utf-8 -*-
"""
upload_to_strava.py
=================
Main class of the application. This file is the one executed to upload the
endomondo activities to strava from the export folder.
"""
from configparser import NoOptionError
from pathlib import Path

import fire
from loguru import logger
from tqdm import tqdm

from parsers.endomondo import retrieve_json_data, get_activity_type
from src.utils.config_handler import init_app
from src.utils.parameters import PATH, ACTIVITIES
from src.utils.strava import get_strava_client


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

    # Check that the folder exist
    if path:
        activities_folder = path
    else:
        try:
            activities_folder = app_config.get(ACTIVITIES, PATH)
            if not activities_folder:
                logger.error('Set the activities folder in the configuration file.')
                raise ValueError('The activities folder retrieved is not valid: {}',
                                 activities_folder)
        except NoOptionError:
            raise ValueError('The activities folder has not been set in the configuration.')

    activity_files = Path(activities_folder).rglob('*.tcx')
    activity_files = [activity.stem for activity in activity_files]
    activity_files = sorted(activity_files, reverse=True)

    logger.info('The number of activity files to upload is {}.', len(activity_files))

    for activity in tqdm(activity_files):
        # Load json first to obtain the data that will be sent along the tcx
        activity_data = retrieve_json_data(activities_folder, activity)
        activity_type = get_activity_type(activity_data)
        print('afas')


if __name__ == '__main__':
    fire.Fire(upload)
