import requests
from .utils import build_url

class Connect():
    def __init__(self, url):
        self.url = url

    def get_account(self, address: str, block:str = "best") -> dict:
        ''' Query account status against the best (or your choice) block '''
        url = build_url(self.url, f'/accounts/{address}?revision={block}')
        r = requests.get(url, headers={'accept':'application/json'})
        if not (r.status_code == 200):
            raise Exception(f'Cant connect to {url}, error {r.text}')
        return r.json()

    def get_block(self, id_or_number: str = 'best') -> dict:
        ''' Get a block, default get "best" block '''
        url = build_url(self.url, f'blocks/{id_or_number}')
        r = requests.get(url, headers={'accept':'application/json'})
        if not (r.status_code == 200):
            raise Exception(f'Cant connect to {url}, error {r.text}')
        return r.json()