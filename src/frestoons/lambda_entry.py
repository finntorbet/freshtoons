import logging
import os
import base64

from api import User
from exceptions import FailedSpotifyAPICall
from persistence import upload_users, retrieve_users

def get_client_b64():
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')

    client_str = f"{client_id}:{client_secret}"
    return base64.urlsafe_b64encode(client_str.encode()).decode()


def update(event, context):
    """
    TODO: Add documentation
    :return:
    """

    logging.getLogger().setLevel(level=logging.INFO)

    users = retrieve_users()

    def update_user_data(user_to_check: User):
        users.loc[users['user_id'] == user_to_check.user_id, 'access_token'] = user_to_check.access_token
        users.loc[users['user_id'] == user_to_check.user_id, 'refresh_token'] = user_to_check.refresh_token
        users.loc[users['user_id'] == user_to_check.user_id, 'playlist_id'] = user_to_check.playlist_id

    client_b64 = get_client_b64()

    for index, row in users.iterrows():

        if not row['refresh_token'] and not row['access_token']:
            continue

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
            else:
                logging.info(f'Playlist has been deleted for user {user.user_id}')
                # TODO: Add 'users.drop(index, inplace=True)' to delete user from dataframe
                # Consider that this would delete the refresh token as well, requiring re-authentication for the application
                # Perhaps an active flag would be more applicable, but then how to turn that back on?
                user.access_token = None
                user.refresh_token = None

        except FailedSpotifyAPICall as err:
            logging.error(f'Spotify API call failing with code {err.status_code}: {err.json}')
            continue

        update_user_data(user)

    upload_users(users)

def add(event, context):
    """
    TODO: Add documentation
    :return:
    """

    logging.getLogger().setLevel(level=logging.INFO)

    client_b64 = get_client_b64()

    users = retrieve_users()

    user_id = event.get('user_id', None)
    access_token = event.get('access_token', None)
    refresh_token = event.get('refresh_token', None)

    if user_id is None or access_token is None or refresh_token is None:
        # Add suitable fail logic
        pass

    existing_user = users.loc[user_id]
    if existing_user is None:

        new_user = User(
            access_token=access_token, 
            refresh_token=refresh_token, 
            user_id=user_id, 
            client_b64=client_b64
        )

    else:

         new_user = User(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=row['user_id'],
            playlist_id=row['playlist_id'],
            playlist_size=row['size'],
            client_b64=client_b64
        )

    new_user = {'Courses':'Hyperion', 'Fee':24000, 'Duration':'55days', 'Discount':1800}
    df2 = df.append(new_row, ignore_index=True)




