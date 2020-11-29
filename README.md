# Endomondo Strava migrator [![Maintainability](https://api.codeclimate.com/v1/badges/279fa5ad0f12febce0a7/maintainability)](https://codeclimate.com/github/adrigrillo/endomondo-strava-migrator/maintainability)

Small Python application to upload the workouts from Endomondo to Strava. As Endomondo is shutting down the 31st of December 2020, this python script is created to upload all the workouts from this platform to Strava. It uses the data export file that can be requested at https://www.endomondo.com/settings/account/archive.
 
It is intended for personal use and has its limitations. Feel free to use it however you like. If you have any comments, questions or want to help, do not hesitate to contact me.

## Requirements
You need Python 3, I personally used 3.8 for this project, and the packages from the `requirements.txt` file, that could be installed using `pip install -r requirements.txt`.
 
With respect to [stravalib](https://github.com/hozn/stravalib), it is possible that you need to install manually an updated version (check [PR #207](https://github.com/hozn/stravalib/pull/207)) as I had to add some activities by the time I developed the script. 
You can use my forked version in https://github.com/adrigrillo/stravalib that is the one I used to upload all my activities, install it by following the [instructions in the readme](https://github.com/adrigrillo/stravalib#building-from-sources).

## Instructions
1. Create a Strava application.
2. Set the Client ID and the Secret of your application in the `config.ini` file under the folder config. Additionally, set the location of the workout folder from the uncompressed export folder.
3. Get the access token by:
    1. Opening the terminal in the `src` folder and running the script by `python request_auth.py`.
    2. A browser windows will open requesting permission to upload new activities to your strava account, accept them and check if the file `config/code_id.txt` have been created. If so, you can close the browser tab.
4. Upload the activities by running `python upload_to_strava.py`.

## API Limitations
The Strava API limits the request to 100 every 15 minutes and 1000 per day.
This script handles automatically the fifteen minutes limitation by sleeping the remaining time until the rest can be uploaded.
However, it does not handle the thousand request peer day limitation. Therefore, if you have more than 1000 activities in Endomondo you will need more than one day and several execution to upload them all.

## Activity type trasformation
Endomondo allowed logging more activities than Strava currently supports. Therefore, in `src/transform/endomondo_strava.py` there is a dictionary that relates the Endomondo types with the Strava ones. In order to check your activities, you can run `python endomondo_analyzer.py` that generates a file in the log folder with the unique activity types present in your history of workouts. Then, you can check the [Strava activity types](https://developers.strava.com/docs/reference/#api-models-ActivityType) and select the most similar option.

