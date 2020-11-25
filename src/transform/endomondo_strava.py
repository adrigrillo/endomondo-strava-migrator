# Endomondo-Strava activities equivalence
from loguru import logger

_ACTIVITIES = {
    'WALKING': 'Walk',
    'RUNNING': 'Run',
    'PADDLE_TENNIS': 'Workout',
    'MOUNTAIN_BIKING': 'Ride',
    'TREADMILL_WALKING': 'VirtualRun',
    'CYCLING_SPORT': 'Ride',
    'AEROBICS': 'Workout',
    'CYCLING_TRANSPORTATION': 'Ride',
    'CROSSFIT': 'Workout',
    'TREADMILL_RUNNING': 'VirtualRun',
    'CROSS_TRAINING': 'Workout',
    'ROWING_INDOOR': 'Rowing',
    'ROWING': 'Rowing',
    'SPINNING': 'VirtualRide',
    'WEIGHT_TRAINING': 'WeightTraining',
    'SWIMMING': 'Swim',
    'SOCCER': 'Soccer'
}


def transform_activity(endomondo_activity: str) -> str:
    """ Transform the Endomondo activity type to Strava activity type.

    Args:
        endomondo_activity (str): Activity type string obtained from the Endomondo
         data.

    Returns:
        str: Strava activity type.
    """
    strava_activity = _ACTIVITIES.get(endomondo_activity)
    logger.debug('{} transformed to {}.', endomondo_activity, strava_activity)
    return strava_activity
