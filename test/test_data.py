from data import User
import responses


class TestCreatePlaylist:

    @responses.activate
    def test_happy_path(self):
        responses.add(**{
            'method': responses.POST,
            'url': 'https://api.spotify.com/v1/users/111/playlists',
            'body': '{}',
            'status': 200,
            'content_type': 'application/json'
        })

        test_user = User('', '', '111', '')

        test_user.create_playlist('')

    @responses.activate
    def test_invalid_token(self):
        responses.add(**{
            'method': responses.POST,
            'url': 'https://api.spotify.com/v1/users/111/playlists',
            'body': '{}',
            'status': 401,
            'content_type': 'application/json'
        })

        test_user = User('', '', '111', '')

        test_user.create_playlist('')
