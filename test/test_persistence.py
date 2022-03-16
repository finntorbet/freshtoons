from io import StringIO

import boto3
import pandas as pd
from moto import mock_s3
from pandas.testing import assert_frame_equal

from persistence import upload_users, retrieve_users


@mock_s3
def test_upload_users_happy_path():
    conn = boto3.resource('s3')
    conn.create_bucket(Bucket='testbucket')
    expected = pd.DataFrame({
                     'A': ['1'],
                     'B': ['2']
                 })

    upload_users(expected, bucket='testbucket')

    csv_string = conn.Object('testbucket', 'users.csv').get()['Body'].read().decode('utf-8')
    actual = pd.read_csv(StringIO(csv_string), dtype=object)

    assert_frame_equal(expected, actual)


@mock_s3
def test_retrieve_users_happy_path():
    conn = boto3.resource('s3')
    conn.create_bucket(Bucket='testbucket')
    expected = pd.DataFrame({
        'A': ['1'],
        'B': ['2']
    })

    csv_buffer = StringIO()
    expected.to_csv(csv_buffer, index=False)
    conn.Object('testbucket', 'users.csv').put(
        Body=csv_buffer.getvalue()
    )

    actual = retrieve_users(bucket='testbucket')

    assert_frame_equal(expected, actual)
