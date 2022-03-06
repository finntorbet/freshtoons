from requests import post
from exceptions import FailedTokenRefresh
import logging


class User:

    def __init__(self, access_token, refresh_token, user_id, client_b64, playlist_id=None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.playlist_id = playlist_id
        self.client_b64 = client_b64

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
        res = post(
            url='https://api.spotify.com/v1/users/' + self.user_id + '/playlists',
            json={
                'name': playlist_name,
                'public': 'false',
                'collaborative': 'false',
                'description': 'The latest from the like button!'
            },
            headers={
                'Authorization': 'Bearer ' + self.access_token,
                'Content-Type': 'application/json'
            }
        )
        return res.status_code, res.json()
