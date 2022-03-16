import responses
from responses.matchers import json_params_matcher, header_matcher

from api import User


class Test_CreatePlaylist:
    @responses.activate
    def test_happy_path(self):
        id = "123"

        responses.add(
            **{
                'method': responses.POST,
                'url': 'https://api.spotify.com/v1/users/111/playlists',
                'body': '{"id": "' + id + '"}',
                'status': 200,
                'content_type': 'application/json'
            },
            match=[
                header_matcher({
                    'Authorization': 'Bearer access_token',
                    'Content-Type': 'application/json'
                }),
                json_params_matcher({
                    'name': 'test name',
                    'public': 'false',
                    'collaborative': 'false',
                    'description': 'The latest from the like button!'
                })
            ]
        )

        test_user = User(access_token='access_token', refresh_token='', user_id='111', playlist_id='',
                         playlist_size='', client_b64='')

        test_user.create_playlist('test name')

        assert len(responses.calls) == 1

        assert responses.calls[0].request.url == 'https://api.spotify.com/v1/users/111/playlists'
        assert test_user.playlist_id == id


class Test_PlaylistStillExists:

    def add_response(self, items):
        body = '{"items": ['
        for playlist_id in items:
            body = body + '{"name":"a name", "id": "' + playlist_id + '"}'
            if not playlist_id == items[len(items) - 1]:
                body = body + ','
        body = body + ']}'

        responses.add(
            **{
                'method': responses.GET,
                'url': 'https://api.spotify.com/v1/me/playlists',
                'body': body,
                'status': 200,
                'content_type': 'application/json'
            },
            match=[
                header_matcher({
                    'Authorization': 'Bearer access_token',
                    'Content-Type': 'application/json'
                })
            ]
        )

    @responses.activate
    def test_happy_path(self):
        playlist_id_to_match = 'id_to_match'

        self.add_response(['false', playlist_id_to_match, 'something'])

        test_user = User(access_token='access_token', refresh_token='', user_id='111', playlist_id=playlist_id_to_match,
                         playlist_size='', client_b64='')

        result = test_user.playlist_still_exists()

        assert len(responses.calls) == 1

        assert responses.calls[0].request.url == 'https://api.spotify.com/v1/me/playlists'
        assert result

    @responses.activate
    def test_false(self):
        self.add_response([])

        test_user = User(access_token='access_token', refresh_token='', user_id='111', playlist_id='',
                         playlist_size='', client_b64='')

        result = test_user.playlist_still_exists()

        assert len(responses.calls) == 1

        assert responses.calls[0].request.url == 'https://api.spotify.com/v1/me/playlists'
        assert not result


class Test_GetLikedSongs:
    def add_response(self, items, playlist_size):
        body = '{"items": ['
        for uri in items:
            body = body + '{"track":{"uri":"' + uri + '"}}'
            if not uri == items[len(items) - 1]:
                body = body + ','
        body = body + ']}'

        responses.add(
            **{
                'method': responses.GET,
                'url': 'https://api.spotify.com/v1/me/tracks?limit=' + str(playlist_size),
                'body': body,
                'status': 200,
                'content_type': 'application/json'
            },
            match=[
                header_matcher({
                    'Authorization': 'Bearer access_token',
                    'Content-Type': 'application/json'
                })
            ]
        )

    @responses.activate
    def test_happy_path(self):
        expected = ['uri_1', 'uri_2', 'uri_3']
        playlist_size = 3

        self.add_response(expected, playlist_size)

        test_user = User(access_token='access_token', refresh_token='', user_id='111', playlist_id='',
                         playlist_size=playlist_size, client_b64='')

        result = test_user.get_liked_songs()

        assert len(responses.calls) == 1

        assert responses.calls[0].request.url == 'https://api.spotify.com/v1/me/tracks?limit=' + str(playlist_size)
        assert len(result) == 3
        result.sort()
        expected.sort()
        assert result == expected

    @responses.activate
    def test_get_liked_songs_large_return(self):
        expected = ['uri_1', 'uri_2', 'uri_3']
        playlist_size = 3

        actual_return_list = expected.copy()
        actual_return_list.append('uri_4')
        actual_return_list.append('uri_5')

        self.add_response(actual_return_list, playlist_size)

        test_user = User(access_token='access_token', refresh_token='', user_id='111', playlist_id='',
                         playlist_size=3, client_b64='')

        result = test_user.get_liked_songs()

        assert len(responses.calls) == 1

        assert responses.calls[0].request.url == 'https://api.spotify.com/v1/me/tracks?limit=' + str(playlist_size)
        assert len(result) == playlist_size
        result.sort()
        expected.sort()
        assert result == expected

    @responses.activate
    def test_get_liked_songs_large_playlist_size(self):
        expected = ['uri_1', 'uri_2', 'uri_3']
        playlist_size = 5

        self.add_response(expected, playlist_size)

        test_user = User(access_token='access_token', refresh_token='', user_id='111', playlist_id='',
                         playlist_size=playlist_size, client_b64='')

        result = test_user.get_liked_songs()

        assert len(responses.calls) == 1

        assert responses.calls[0].request.url == 'https://api.spotify.com/v1/me/tracks?limit=' + str(playlist_size)
        result.sort()
        expected.sort()
        assert result == expected


class Test_UpdatePlaylist:
    comma_code = '%2C'
    colon_code = '%3A'

    def add_response(self, items, playlist_id):
        params = ''
        for song in items:
            params = params + song + ','

        params = params.replace(',', self.comma_code)
        params = params.replace(':', self.colon_code)

        responses.add(
            **{
                'method': responses.PUT,
                'url': 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks?uris=' + params,
                'status': 200,
                'content_type': 'application/json'
            },
            match=[
                header_matcher({
                    'Authorization': 'Bearer access_token',
                    'Content-Type': 'application/json'
                })
            ]
        )

    @responses.activate
    def test_happy_path(self, mocker):
        playlist_id = '111'

        self.add_response(
            ['song:1', 'song:2', 'song:3'],
            playlist_id
        )

        mocker.patch.object(User, 'get_liked_songs', return_value=['song:1', 'song:2', 'song:3'])

        test_user = User(access_token='access_token', refresh_token='', user_id='', playlist_id=playlist_id,
                         playlist_size='', client_b64='')

        test_user.update_playlist()

        assert len(responses.calls) == 1
        assert responses.calls[
                   0].request.url == 'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks?uris=song%3A1%2Csong%3A2%2Csong%3A3%2C'


# TODO Test get_fresh_access_token
class Test_GetFreshAccessToken:
    def test_happy_path(self):
        pass

    def test_invalid_refresh(self):
        pass


# TODO  Test Callers
class Test_Callers:
    def test_post(self):
        pass

    def test_get(self):
        pass

    def test_put(self):
        pass
