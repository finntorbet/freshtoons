import configparser
import logging
import base64
from data import User
from exceptions import FailedSpotifyAPICall

if __name__ == '__main__':
    logging.basicConfig(filename="output.log", level=logging.DEBUG)

    cfg = configparser.ConfigParser()
    cfg.read('config')


    def update_user_data(user: User):
        if not cfg['finn']['access_token'] == user.access_token:
            cfg.set("finn", "access_token", user.access_token)
            cfg.write(open('config', 'w'))
            logging.info('New Token Written to File')
        if not cfg['finn']['playlist_id'] == user.playlist_id:
            cfg.set("finn", "playlist_id", user.playlist_id)
            cfg.write(open('config', 'w'))
            logging.info('New Playlist ID Written to File')


    client_id = cfg['app']['client_id']
    client_secret = cfg['app']['client_secret']
    client_str = f"{client_id}:{client_secret}"
    client_b64 = base64.urlsafe_b64encode(client_str.encode()).decode()

    access_token = cfg['finn']['access_token']
    refresh_token = cfg['finn']['refresh_token']
    user_id = cfg['finn']['user_id']
    playlist_id = cfg['finn']['playlist_id']

    user = User(access_token, refresh_token, user_id, client_b64, playlist_id)

    if playlist_id == '':
        user.create_playlist('fresh toons')

    try:
        if user.poll_playlist():
            user.update_playlist()
        else:
            logging.info(f'Playlist has been deleted for user {user.user_id}')
            quit()
    except FailedSpotifyAPICall as err:
        logging.error(f'Spotify API call failing with code {err.status_code}: {err.json}')
        pass

    update_user_data(user)
