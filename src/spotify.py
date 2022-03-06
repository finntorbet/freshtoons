import logging as log
from requests import get, post
from exceptions import FailedTokenRefresh
from datetime import datetime

url = 'https://api.spotify.com/v1'


def create_playlist(access_token, playlist_name, user_id):
    res = post(
        url=url + '/users/' + user_id + '/playlists',
        json={
            'name': playlist_name,
            'public': 'false',
            'collaborative': 'false',
            'description': 'The latest from the like button!'
        },
        headers={
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
    )
    return res.status_code, res.json()


def get_liked_songs(access_token, ):
    print('Get liked songs...')






class SpotifyDAO:

    def __init__(self, client_id, client_secret):
        # self.expiry_time = None
        # self.refresh_token = None
        # self.access_token = None
        # client_creds = f"{client_id}:{client_secret}"
        # self.client_creds_b64 = base64.b64encode(f"{client_id}:{client_secret}".encode())
        self.client_id = client_id
        self.client_secret = client_secret

    def check_for_valid_access_token(self):
        if self.access_token is None or datetime.now() > self.expiry_time:
            self.authenticate_client()

    def update_playlist(user_token, playlist_id):
        log.info(f'Hello World {user_token} & {playlist_id}')

    # def request_user_authorization(self):
    #     try:
    #         req = get(
    #             'https://accounts.spotify.com/authorize',
    #             params={
    #                 'client_id': self.client_id,
    #                 'response_type': 'code',
    #                 'redirect_uri': '',
    #                 'scopes':
    #             },
    #             headers={'Authorization': f'Basic {self.client_creds_b64}'}
    #         )
    #         token_response = req.json()
    #         self.access_token = token_response['access_token']
    #         self.expires_in = token_response['expires_in']
    #         self.refresh_token = token_response['refresh_token']
    #
    #     except HTTPError as http_err:
    #         log.error(f'HTTP error occured: {http_err}')
    #
    # def authenticate(self):
    #     log.info("Registered User")
