import os
from unittest import mock

import pytest
import pandas as pd

from api import User
from lambda_entry import update

expected_client_64 = 'MTIzNDo0MzIx'

@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    mock.patch.dict(os.environ, {"client_id": "1234"})
    mock.patch.dict(os.environ, {"client_secret": "4321"})

# TODO Test top level happy path with mocked commponents
def test_update_happy_path(mocker):
    pass
    # Mock persistence.retrieve_users()
    # x = pd.DataFrame({
    #     'user_id': 'a_user_id',
    #     'playlist_id': 'a_playlist_id',
    #     'access_token': 'a_access_token',
    #     'refresh_token': 'a_refresh_token',
    #     'size': None,
    #     'date_offset': None,
    # }, index=None)
    # mocker.patch('persistence.retrieve_users', return_value=x)
    #
    # # Mock user.playlist_still_exists()
    # mocker.patch.object(User, 'playlist_still_exists', return_value=True)
    #
    # # Mock user.update_playlist()
    # mocker.patch.object(User, 'update_playlist', return_value=None)
    #
    # # Mock persistence.upload_users()
    # mocker.patch('persistence.upload_users', return_value=None)
    #
    # update(None, None)

    # Check
    #   - correct client b64 is created
    #   - User is created with correct info
    #   - user.update_playlist is called
    #   - the csv is updated correctly
    #   - the csv is sent to upload_users

def test_empty_users():
    pass
    # Check
    #   - no User objects are created or called

def test_empty_playlistsize():
    pass
    # Check
    #   -

def test_deleted_playlist():
    pass