import logging
from abc import ABC, abstractmethod

"""
Methods to handle all data persistence and retrieval

@author Finn Torbet
"""

class PersistenceInterface(ABC):
    @abstractmethod
    def retrieve_users(self, *args, **kwargs):
        pass

    @abstractmethod
    def upload_users(self, users, *args, **kwargs):
        pass

class S3Persistence(PersistenceInterface):
    from io import StringIO

    import boto3
    import pandas as pd

    def s3_retrieve_users(self, bucket='freshtoons'):
        s3 = boto3.client('s3')
        logging.debug(f'Trying to retrieve users.csv from {bucket}...')
        csv_obj = s3.get_object(Bucket=bucket, Key='users.csv')
        logging.debug(f'Retrieved users.csv from {bucket}!')
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        return pd.read_csv(StringIO(csv_string), index_col=False, dtype=object, keep_default_na=False)


    def upload_users(self, users, bucket='freshtoons'):
        s3 = boto3.client('s3')
        csv_buffer = StringIO()
        logging.debug(f'Uploading users.csv to {bucket}...')
        users.to_csv(csv_buffer, index=False)
        logging.debug(f'Uploaded users.csv to {bucket}!')
        s3.put_object(
            Body=csv_buffer.getvalue(),
            Bucket=bucket,
            Key='users.csv'
        )

class LocalPersistence(PersistenceInterface):
    import csv

    # Rewrite the csv to return 
    # [
    #   {"access_token": "", "x":"y"},
    #   {"access_token": "", "x":"y"},
    #   ...
    # ]

    def __init__():
        self.local_path = os.getenv("LOCAL_STORAGE_PATH")

     def retrieve_users():
        if os.path.exists(self.local_path):
            logging.debug(f"Loading file: {self.local_path}")
            with open(self.local_path):
                return csv.reader(self.local_path, delimiter=",")
        else:
            logging.error("Invalid path!")
            os.exit(1)

    def upload_users(users, bucket='freshtoons'):
        if os.path.exists(self.local_path):
            logging.debug(f"Saving file: {self.local_path}")
            with open(self.local_path, "w") as csvfile:
                writer = csv.writer(csvfile)
                csv.writer(self.local_path)
            users.to_csv(self.local_path,)
        else:
            logging.error("Invalid path!")
            os.exit(1)

