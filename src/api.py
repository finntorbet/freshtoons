from requests import post, get, put
from exceptions import FailedTokenRefresh, FailedSpotifyAPICall
import logging
import pandas as pd

api_url = 'https://api.spotify.com/v1/'

# 20 is the default, but explicitly declaring it helps robustability
PLAYLIST_PAGE_SIZE = 20


class User:
    """
    The User class represents one user with all their API relevant data.
    The user can refresh its own token and call common api functions for the user it is created for.
    """

    def __init__(self, access_token, refresh_token, user_id, client_b64, playlist_id, playlist_size):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.playlist_id = playlist_id
        self.client_b64 = client_b64
        if playlist_size is None or playlist_size == '' or pd.isnull(playlist_size):
            self.playlist_size = 20
        else:
            self.playlist_size = int(playlist_size)

    def post_caller(self, url, headers=None, data=None, json=None):
        """
        A generic method to handle POST calls

        :param url: url to call
        :param headers: headers to include in the call
        :param data: data to be included in the call
        :param json: json to be included in the call
        :return: the json response
        :exception FailedSpotifyAPICall: If the response is not a success, after having refreshed the token, then this exception is thrown
        """
        res = post(url=url, headers=headers, data=data, json=json)

        if res.status_code == 401:
            logging.error('Invalid Token! Requesting refresh...')
            self.get_fresh_access_token()
            logging.info('New Token Acquired')
            headers['Authorization'] = 'Bearer ' + self.access_token
            res = post(url=url, headers=headers, data=data, json=json)

        if res.status_code not in (200, 201):
            logging.error(f"Failed to call POST : {url} with error code {res.status_code} : {res.json()}")
            raise FailedSpotifyAPICall(res.status_code, res.json())
        else:
            return res.json()

    def get_caller(self, url, headers, params=None):
        """
        A generic method to handle GET calls

        :param url: url to call
        :param headers: headers to include in the call
        :param params: params to include in the call
        :return: the json response
        :exception FailedSpotifyAPICall: If the response is not a success, after having refreshed the token, then this exception is thrown
        """
        res = get(url=url, headers=headers, params=params)

        if res.status_code == 401:
            logging.error('Invalid Token! Requesting refresh...')
            self.get_fresh_access_token()
            logging.info('New Token Acquired')
            headers['Authorization'] = 'Bearer ' + self.access_token
            res = get(url=url, headers=headers, params=params)

        if res.status_code not in (200, 201):
            logging.error(f"Failed to call GET : {url} with error code {res.status_code} : {res.json()}")
            raise FailedSpotifyAPICall(res.status_code, res.json())
        else:
            return res.json()

    def put_caller(self, url, headers=None, params=None, json=None):
        """
        A generic method to handle PUT calls

        :param url: url to call
        :param headers: headers to include in the call
        :param params: params to be included in the call
        :param json: json to be included in the call
        :return: the json response
        :exception FailedSpotifyAPICall: If the response is not a success, after having refreshed the token, then this exception is thrown
        """
        res = put(url=url, headers=headers, params=params, json=json)

        if res.status_code == 401:
            logging.error('Invalid Token! Requesting refresh...')
            self.get_fresh_access_token()
            logging.info('New Token Acquired')
            headers['Authorization'] = 'Bearer ' + self.access_token
            res = put(url=url, headers=headers, params=params, json=json)

        if res.status_code not in (200, 201):
            logging.error(f"Failed to call PUT : {url} with error code {res.status_code} : {res.json()}")
            raise FailedSpotifyAPICall(res.status_code, res.json())

    def get_fresh_access_token(self):
        """
        Method to retrieve a fresh access token (and subsequent refresh token) for this user.

        :exception FailedTokenRefresh: If the refresh API operation fails, the method throws this exception
        """
        res = post(
            url='https://accounts.spotify.com/api/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            },
            headers={
                'Authorization': 'Basic ' + self.client_b64
            }
        )
        if res.status_code in (200, 201):
            resp_body = res.json()
            self.access_token = resp_body['access_token']
            logging.info(f"Set new token: {self.access_token}")
            if 'refresh_token' in resp_body:
                self.refresh_token = resp_body['refresh_token']
        else:
            logging.error(f"Failed to get a refreshed token with error code {res.status_code} : {res.json()}")
            raise FailedTokenRefresh

    def create_playlist(self, playlist_name):
        """
        Creates a playlist to be refreshed with recent liked songs.
        Uses: https://developer.spotify.com/documentation/web-api/reference/create-playlist

        :param playlist_name: Name of the newly created playlist.
        """

        url = api_url + 'users/' + self.user_id + '/playlists'
        json = {
            'name': playlist_name,
            'public': 'false',
            'collaborative': 'false',
            'description': 'The latest from the like button!'
        }
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json'
        }

        response_json = self.post_caller(url=url, headers=headers, json=json)
        self.playlist_id = response_json['id']

    def playlist_still_exists(self):
        """
        Method to check if the playlist the program has stored for this user has been deleted or not.
        Uses: https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists

        :return: boolean that indicates if the playlist on record still exists or not.
        """
        url = api_url + 'me/playlists'
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json'
        }

        more_pages = True
        offset = 0
        while more_pages:
            response_json = self.get_caller(url=url, headers=headers, params={"offset": offset, "limit": PLAYLIST_PAGE_SIZE})
            for playlist in response_json['items']:
                if self.playlist_id == playlist['id']:
                    return True

            offset = offset + PLAYLIST_PAGE_SIZE

            if response_json['next'] is None:
                more_pages = False
        return False

    def get_liked_songs(self):
        """
        Retrieves this user's liked songs in chronological order (date added desc) as a list of song ids.
        Uses: https://developer.spotify.com/documentation/web-api/reference/save-tracks-user

        :return ids: list of unique ids of size self.playlist_size
        """
        url = api_url + 'me/tracks'
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json'
        }
        params = {'limit': self.playlist_size}

        response_json = self.get_caller(url=url, headers=headers, params=params)

        track_items = response_json['items']
        ids = []
        counter = 0
        while counter < self.playlist_size and counter < len(track_items):
            ids.append(track_items[counter]['track']['uri'])
            counter = counter + 1

        return ids

    def update_playlist(self):
        """
        Method to update a playlist with the top liked songs returned from the get_liked_songs method.
        Uses: https://developer.spotify.com/documentation/web-api/reference/reorder-or-replace-playlists-tracks
        """
        liked_songs = self.get_liked_songs()
        new_playlist_str = ''
        for song in liked_songs:
            new_playlist_str = new_playlist_str + song + ','

        url = api_url + 'playlists/' + self.playlist_id + '/tracks'
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json'
        }
        params = {
            'uris': new_playlist_str
        }

        self.put_caller(url=url, headers=headers, params=params)
