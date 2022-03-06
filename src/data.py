from requests import post, get, put
from exceptions import FailedTokenRefresh, FailedSpotifyAPICall
import logging

api_url = 'https://api.spotify.com/v1/'


class User:

    def __init__(self, access_token, refresh_token, user_id, client_b64, playlist_id=None, playlist_size=20):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.playlist_id = playlist_id
        self.client_b64 = client_b64
        if playlist_size > 50:
            playlist_size = 50
        self.playlist_size = playlist_size

    def get_fresh_access_token(self):
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
            self.access_token = res.json()['access_token']
        else:
            logging.error(f"Failed to get a refreshed token with error code {res.status_code} : {res.json()}")
            raise FailedTokenRefresh

    def create_playlist(self, playlist_name):

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

        res = post(url=url, json=json, headers=headers)

        if res.status_code == 401:
            logging.error('Invalid Token! Requesting refresh...')
            self.get_fresh_access_token()
            logging.info('New Token Acquired')
            headers['Authorization'] = 'Bearer ' + self.access_token
            res = post(url=url, json=json, headers=headers)

        if res.status_code not in (200, 201):
            logging.error(f"Failed to call create_playlist with error code {res.status_code} : {res.json()}")
            raise FailedSpotifyAPICall(res.status_code, res.json())
        else:
            self.playlist_id = res.json()['id']

    def poll_playlist(self):
        url = api_url + 'me/playlists'
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json'
        }

        res = get(url=url, headers=headers)

        if res.status_code == 401:
            logging.error('Invalid Token! Requesting refresh...')
            self.get_fresh_access_token()
            logging.info('New Token Acquired')
            headers['Authorization'] = 'Bearer ' + self.access_token
            res = get(url=url, headers=headers)

        if res.status_code not in (200, 201):
            logging.error(f"Failed to call poll_playlist with error code {res.status_code} : {res.json()}")
            raise FailedSpotifyAPICall(res.status_code, res.json())

        for playlist in res.json()['items']:
            if self.playlist_id in playlist['id']:
                return True
        return False

    def get_liked_songs(self):
        """
        Retrieves this user's liked songs in chronological order (most recent to recent)
        as a list of song ids
        :return: list of unique ids of size self.playlist_size
        """
        url = api_url + 'me/tracks'
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json'
        }
        param = {'limit': self.playlist_size}

        res = get(url=url, headers=headers, params=param)

        if res.status_code == 401:
            logging.error('Invalid Token! Requesting refresh...')
            self.get_fresh_access_token()
            logging.info('New Token Acquired')
            headers['Authorization'] = 'Bearer ' + self.access_token
            res = get(url=url, headers=headers, params=param)

        if res.status_code not in (200, 201):
            logging.error(f"Failed to call poll_playlist with error code {res.status_code} : {res.json()}")
            raise FailedSpotifyAPICall(res.status_code, res.json())

        track_items = res.json()['items']
        ids = []

        counter = 0
        while counter < self.playlist_size or counter < len(track_items):
            ids.append(track_items[counter]['track']['uri'])
            counter = counter + 1

        return ids

    def update_playlist(self):
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

        res = put(url=url, headers=headers, params=params, json={})

        if res.status_code == 401:
            logging.error('Invalid Token! Requesting refresh...')
            self.get_fresh_access_token()
            logging.info('New Token Acquired')
            headers['Authorization'] = 'Bearer ' + self.access_token
            res = put(url=url, headers=headers, params=params, json={})

        if res.status_code not in (200, 201):
            logging.error(f"Failed to call update_playlist with error code {res.status_code} : {res.json()}")
            raise FailedSpotifyAPICall(res.status_code, res.json())
