import json
from json import JSONDecodeError
from tokenize import TokenError

import requests


class Tokenman:
    def __init__(self, token: str | None = None):
        self.token = token if token is not None else ''

    def get_token(self):
        if self.token == '':
            if not self.renew_token():
                raise TokenError()
        return self.token


    def renew_token(self):
        try:
            data = requests.post('http://host.docker.internal:8180/api/token', json={'user_id': 1,
                                                                                 'password': 'apply123!'}).json()
        except JSONDecodeError:
            return False
        
        if data.get('success', False):
            self.token = data['data'].get('token', ' ')
            return True
        return False
