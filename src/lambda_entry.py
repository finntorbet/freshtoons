import logging
import os
import base64

from api import User
from exceptions import FailedSpotifyAPICall
from persistence import upload_users, retrieve_users


def update(event, context):
    """
    TODO: Add documentation
    :return:
    """

    logging.getLogger().setLevel(level=logging.DEBUG)

    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')

    users = retrieve_users()

    def update_user_data(user_to_check: User):
        users.loc[users['access_token'] != [user_to_check.access_token], 'access_token'] = user_to_check.access_token
        users.loc[users['refresh_token'] != [user_to_check.refresh_token], 'refresh_token'] = user_to_check.refresh_token
        users.loc[users['playlist_id'] != [user_to_check.playlist_id], 'playlist_id'] = user_to_check.playlist_id

    client_str = f"{client_id}:{client_secret}"
    client_b64 = base64.urlsafe_b64encode(client_str.encode()).decode()

    for index, row in users.iterrows():

        user = User(
            access_token=row['access_token'],
            refresh_token=row['refresh_token'],
            user_id=row['user_id'],
            playlist_id=row['playlist_id'],
            playlist_size=row['size'],
            client_b64=client_b64
        )

        try:
            if user.playlist_still_exists():
                user.update_playlist()
                update_user_data(user)
            else:
                logging.info(f'Playlist has been deleted for user {user.user_id}')
                # TODO: Add 'users.drop(index, inplace=True)' to delete user from dataframe
                continue
        except FailedSpotifyAPICall as err:
            logging.error(f'Spotify API call failing with code {err.status_code}: {err.json}')
            continue

    upload_users(users)

