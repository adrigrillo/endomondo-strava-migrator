# -*- coding: utf-8 -*-
"""
upload_to_strava.py
=================
Main class of the application. This file is the one executed to upload the
endomondo activities to strava from the export folder.
"""
import json
from collections import Counter

import fire
from loguru import logger
from tqdm import tqdm

from parsers.endomondo import retrieve_json_data, get_activity_type
from utils.config_handler import init_app
from utils.files_handler import retrieve_activities_path, get_activity_files_names
from utils.parameters import SYSTEM, PATH


def analyze_activity_types(path: str = None,
                           config: str = '../config/config.ini'):
    """ This method generates a file with the type of activities and the number
    of times that have been performed.

    Args:
        path (str): path to the folder containing the activities.
        config (str): path to the configuration file.
    """
    app_config = init_app(config)
    activities_folder = retrieve_activities_path(path, app_config)

    activity_files = get_activity_files_names(activities_folder)

    activities_found = list()

    for activity in tqdm(activity_files):
        # Load json first to obtain the data that will be sent along the tcx
        activity_data = retrieve_json_data(activities_folder, activity)
        activity_type = get_activity_type(activity_data)
        activities_found.append(activity_type)

    # Extract the unique values and the number of times that are found
    unique_activities = list(Counter(activities_found).keys())
    number_unique_activities = list(Counter(activities_found).values())
    unique_activities_number = dict(zip(unique_activities, number_unique_activities))

    file_path = f'{app_config.get(SYSTEM, PATH)}/unique_activities_number.json'
    with open(file_path, 'w') as file:
        logger.info('Saving file with the number of activities in `{}`', file_path)
        json.dump(unique_activities_number, file, indent=4)


if __name__ == '__main__':
    fire.Fire(analyze_activity_types)
