import webbrowser
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from socketserver import TCPServer

import fire
from loguru import logger
from stravalib import Client

from utils.config_handler import init_app
from utils.constants import CONFIG_PATH, FALLBACK_PORT, CODE_ID_FILE_NAME
from utils.files_handler import check_folder
from utils.parameters import SYSTEM, PORT
from utils.strava import get_client_id


class StravaAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """ Handles the redirection of the authorization page and parses the
        get request to obtain the code id. The code id is written in the
        temporary path (`TEMP_SAVE_PATH`) with the name (`CODE_ID_FILE_NAME`)
        specified in utils/constants.py.
        """
        path = self.path
        web_path, parameters = path.split('?')
        # Parse if is an authorization call
        if web_path == '/authorization':
            logger.info('Received authorization call')
            code_id = None

            # Search for code_id
            parameters = parameters.split('&')
            for parameter in parameters:
                key, value = parameter.split('=')
                if key == 'code':
                    code_id = value
                    logger.info('code_id: {}', code_id)
                    break

            # If found save
            if code_id:
                file_path = Path(check_folder(CONFIG_PATH), CODE_ID_FILE_NAME)
                with open(file_path, 'w+') as file:
                    file.write(code_id)
                    logger.info('Writing received code_id in {}.', CONFIG_PATH)
                self.send_response(200)

            else:
                logger.warning('code id not found in the request.')
                self.send_response(500)

        # Ignore request
        else:
            self.send_response(200)


def request_code_id(config: str = '../config/config.ini'):
    """ Method that handles the authentication process to request the code id.
    The execution will open the browser to authorize the application to write new
    activities and retrieve the `code_id` that is later used to get an access token
    and import the data.

    Once the code is retrieved the application has to be close using CTRL+C.

    Args:
        config (str): path to the configuration file.
    """
    app_config = init_app(config)
    # Create server
    port = app_config.getint(SYSTEM, PORT, fallback=FALLBACK_PORT)
    server = TCPServer(('', port), StravaAuthHandler)
    logger.debug('The server port is: {}', port)

    # Create first auth request
    client = Client()
    client_id = get_client_id(app_config)
    url = client.authorization_url(client_id=client_id,
                                   redirect_uri=f'http://127.0.0.1:{port}/authorization',
                                   scope='activity:write')
    webbrowser.open(url)
    del client

    # Catch redirection to extract the code
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    logger.info('Closing server.')
    server.server_close()


if __name__ == '__main__':
    fire.Fire(request_code_id)
