# -*- coding: utf-8 -*-
"""
utils/config_handler.py
=================
Utility class to configure the logging system.
"""
import sys
from configparser import ConfigParser

from loguru import logger

from utils.constants import FALLBACK_FILE_NAME, FALLBACK_LOG_LEVEL, FALLBACK_WORKING_FOLDER
from utils.files_handler import generate_output_directory_string, check_folder
from utils.parameters import SYSTEM, FILE_NAME, LOG_LEVEL, PATH

FORMAT = "<green>{time:YYMMDD-HHmmss.SS}</green>|<level>{level:.1}</level>|<cyan>{name}</cyan>:" \
         "<cyan>{function}</cyan>:<cyan>{line}</cyan>|<level>{message}</level>"
ERROR_LEVEL = 'ERROR'


def init_app(config_path: str) -> ConfigParser:
    """ Initializes the application creating a unique folder for the logs and
    setting up the logging configuration.

    Args:
        config_path: path to the configuration file. By default it will be
        located in `strava-upload/config/config.ini`.

    Returns:
        Updated configuration parser with the working path.

    """
    config = ConfigParser(allow_no_value=True)
    config.read(config_path)
    # Retrieves the configuration
    file_name = config.get(SYSTEM, FILE_NAME, fallback=FALLBACK_FILE_NAME)
    log_level = config.get(SYSTEM, LOG_LEVEL, fallback=FALLBACK_LOG_LEVEL)
    working_path = config.get(SYSTEM, PATH, fallback=FALLBACK_WORKING_FOLDER)

    # Configure working folder and logs
    working_path = generate_output_directory_string(working_path)
    check_folder(working_path)
    configure_logger(working_path, file_name, log_level)

    # Set the system path as the working path
    config.set(SYSTEM, PATH, working_path)

    del working_path, log_level
    return config


def configure_logger(working_path: str,
                     file_name: str,
                     level: str) -> None:
    """ Configure the loggers that will be used. It generates a file logger and
    a console logger where all the logs will go and also a error file logger where
    only the errors will go.

    Args:
        working_path (str): Working path of the project, were the results will be
         saved. The error log file will be added error in the name.
        file_name (str): File name where the logs will be saved.
        level (str): Log level of the general logger.
    """
    # Remove console logger
    logger.remove()
    # Create new loggers: console, file and error file
    logger.add(sys.stdout, level=level, format=FORMAT)
    logger.add(f'{working_path}/{file_name}.log', level=level, format=FORMAT)
    logger.add(f'{working_path}/{file_name}_error.log', level=ERROR_LEVEL, format=FORMAT)
    logger.info('Logging system initialized. Level: {}. Folder: {}.', level, working_path)
