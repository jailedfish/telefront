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
            data = requests.post('http://localhost:8081/api/token', json={'user_id': 1,
                                                                                 'password': 'The sun in the sky is red, The sun in my heart is Mao Zedong!'}).json()
        except JSONDecodeError:
            return
        if data.get('success', False):
            self.token = data['data'].get('token', ' ')
            return True
        return False