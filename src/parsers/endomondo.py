# -*- coding: utf-8 -*-
"""
parsers/endomondo.py
=================
Utility class to retrieve the data from the Endomondo json.
"""
import json
from typing import Dict, List

from loguru import logger


def retrieve_json_data(folder_path: str, file_name: str) -> List[Dict]:
    """ Opens the JSON file from Endomondo and returns the data in a dict.

    Args:
        folder_path (str): path to the workouts folder.
        file_name (str): name of the file to open.

    Returns:
        activity_data (List[Dict]): list of dictionaries with the information
         of the workout.
    """
    with open(f'{folder_path}{file_name}.json') as file:
        activity_data = json.load(file)

    return activity_data


def get_activity_type(activity_data: List[Dict]) -> str:
    """ Retrieves the Endomondo activity type from the JSON data.

    Args:
        activity_data (list): list of dictionaries with the information of the workout,
         generated by `parsers.endomondo_json.retrieve_json_data`.

    Returns:
        str: String with the Endomondo activity type.

    """
    activity_type = None
    for field in activity_data:
        activity_type = field.get('sport')
        if activity_type:
            break

    if not activity_type:
        logger.warning('No activity type was found for the file. Setting as `other`.')
        activity_type = 'OTHER'

    logger.debug('The Endomondo activity type is: {}', activity_type)
    return activity_type
