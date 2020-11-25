# -*- coding: utf-8 -*-
"""
utils/files_handler.py
=================
Utility class to handle files and folders.
"""
import os
import random
import string
from configparser import ConfigParser, NoOptionError
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from dateutil.tz import tz
from loguru import logger

from utils.parameters import ACTIVITIES, PATH


def check_folder(path: str) -> str:
    """ Checks if the folder exist and generates it if not.

    :param path: path to the folder to check.
    :return: path to the folder.
    """
    if not os.path.exists(path):
        logger.debug("Creating directory {}", path)
        os.makedirs(path)
    return path


def generate_output_directory_string(working_path: str) -> str:
    """ Generates output folder string in format ``YYMMDD_HHMMSS_ABC``
    that will be appended at the end of working dir.

    The handling of the timestamp can be checked in
    https://docs.python.org/3.6/library/datetime.html#strftime-strptime-behavior.

    Args:
        working_path: str. Working path of the project where the results will be saved.

    Returns:
        unique folder in the working path were results will be saved.

    """
    # Generate output folders with timestamp
    timestamp = datetime.now(tz.tzlocal()).strftime('%y%m%d_%H%M%S')
    job_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))

    return f'{working_path}/{timestamp}_{job_id}'


def retrieve_activities_path(path: Optional[str], app_config: ConfigParser) -> str:
    """ Retrieves the path where the activities are saved. This method takes the
    `path` argument as first choice if it exists. Otherwise, it searches for the
    path in the configuration file, that should be under the "activities" section.

    Args:
        path (str): command line argument that could be set.
        app_config (ConfigParser): app configuration.

    Returns:
        str: if the path exists it is returned.

    Raises:
        ValueError: if the path is not set in the argument and in the
         configuration.

    """
    # Check that the folder exist
    if path:
        logger.trace('Using argument path.')
        activities_folder = path

    else:
        logger.trace('Using configuration path.')
        try:
            activities_folder = app_config.get(ACTIVITIES, PATH)
            if not activities_folder:
                logger.error('Set the activities folder in the configuration file.')
                raise ValueError('The activities folder retrieved is not valid: {}',
                                 activities_folder)
        except NoOptionError:
            raise ValueError('The activities folder has not been set in the configuration.')

    if not Path(activities_folder).exists():
        raise NotADirectoryError(f'The specified path does not exist. Path: `{activities_folder}`')

    logger.info('Using `{}` as activities folder.', activities_folder)

    return activities_folder


def get_activity_files_names(activities_folder: str, file_extension: str = '*.json') -> List[str]:
    """ Obtains the file names of all the activities found in the activities' folder.
    If the file names are dates, the method will sort the list by recent workouts.

    Args:
        activities_folder (str): path where the workouts files are saved.
        file_extension (str): extension of the files. Used to perform the glob operation.

    Returns:
        list(str): ordered list with the names of the files found.

    """
    logger.trace('Searching in `{}` all the workout files in `{}` format.',
                 activities_folder, file_extension)

    activity_files = Path(activities_folder).glob(file_extension)
    activity_files = [activity.stem for activity in activity_files]
    activity_files = sorted(activity_files, reverse=True)

    logger.info('The number of activity files found is {}.', len(activity_files))
    return activity_files
