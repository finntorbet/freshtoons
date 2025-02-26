class FailedTokenRefresh(Exception):
    pass


class FailedSpotifyAPICall(Exception):
    def __init__(self, status_code, json):
        self.status_code = status_code
        self.json = json
        super(f'{status_code}:\t{json}')
