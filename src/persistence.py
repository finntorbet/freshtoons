from io import StringIO

import boto3
import pandas as pd
import logging

"""
Methods to handle all data persistence and retrieval

@author Finn Torbet
"""


def retrieve_users(bucket='freshtoons'):
    s3 = boto3.client('s3')
    logging.debug(f'Trying to retrieve users.csv from {bucket}...')
    csv_obj = s3.get_object(Bucket=bucket, Key='users.csv')
    logging.debug(f'Retrieved users.csv from {bucket}!')
    body = csv_obj['Body']
    csv_string = body.read().decode('utf-8')
    return pd.read_csv(StringIO(csv_string), index_col=False, dtype=object)


def upload_users(users_csv, bucket='freshtoons'):
    s3 = boto3.client('s3')
    csv_buffer = StringIO()
    logging.debug(f'Uploading users.csv to {bucket}...')
    users_csv.to_csv(csv_buffer, index=False)
    logging.debug(f'Uploaded users.csv to {bucket}!')
    s3.put_object(
        Body=csv_buffer.getvalue(),
        Bucket=bucket,
        Key='users.csv'
    )

