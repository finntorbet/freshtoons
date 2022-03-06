import configparser
import logging
import base64
from data import User


def run_func(user: User, func, args):
    logging.info(f'Attempting {func.__name__}...')
    status_code, message = func(*args)
    if status_code == 401:
        logging.error('Invaid Token! Requesting refresh...')
        user.get_fresh_access_token()
        logging.info('New Token Acquired')
        logging.info(f'Attempting {func.__name__} again...')
        status_code, message = func(*args)

    if status_code not in (200, 201):
        logging.error(f"Failed to call {func.__name__} with error code {status_code} : {message}")


if __name__ == '__main__':
    logging.basicConfig(filename="output.log", level=logging.DEBUG)

    cfg = configparser.ConfigParser()
    cfg.read('config')


    def update_token(new_token):
        cfg.set("finn", "access_token", new_token)
        cfg.write(open('config', 'w'))
        logging.info('New Token Written to File')


    client_id = cfg['app']['client_id']
    client_secret = cfg['app']['client_secret']
    client_str = f"{client_id}:{client_secret}"
    client_b64 = base64.urlsafe_b64encode(client_str.encode()).decode()

    access_token = cfg['finn']['access_token']
    refresh_token = cfg['finn']['refresh_token']
    user_id = cfg['finn']['user_id']

    finn = User(access_token, refresh_token, user_id, client_b64)

    run_func(finn, finn.create_playlist, ('fresh toons',))

    update_token(finn.access_token)
