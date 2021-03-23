import copy
from typing import Union
import requests
from .utils import build_url, calc_blockRef, calc_chaintag, calc_nonce, any_emulate_failed, read_vm_gases
from .wallet import Wallet
from thor_devkit import abi, cry, transaction

class Connect():
    ''' Connect to VeChain '''
    def __init__(self, url):
        self.url = url

    def get_account(self, address: str, block:str = "best") -> dict:
        ''' Query account status against the "best" block (or your choice)'''
        url = build_url(self.url, f'/accounts/{address}?revision={block}')
        r = requests.get(url, headers={'accept':'application/json'})
        if not (r.status_code == 200):
            raise Exception(f'Cant connect to {url}, error {r.text}')
        return r.json()

    def get_block(self, id_or_number: str = 'best') -> dict:
        ''' Get a block by id or number, default get "best" block '''
        url = build_url(self.url, f'blocks/{id_or_number}')
        r = requests.get(url, headers={'accept':'application/json'})
        if not (r.status_code == 200):
            raise Exception(f'Cant connect to {url}, error {r.text}')
        return r.json()

    def get_chainTag(self) -> int:
        ''' Fetch ChainTag from the remote network '''
        b = self.get_block(0)
        return calc_chaintag(b['id'][-2:])
    
    def get_tx(self, tx_id: str) -> Union[dict, None]:
        ''' Fetch a transaction, if not found then None '''
        url = build_url(self.url, f'/transactions/{tx_id}')
        r = requests.get(url, headers={'accept':'application/json'})
        if not (r.status_code == 200):
            raise Exception(f'Cant connect to {url}, error {r.text}')
        return r.json()

    def replay_tx(self, tx_id: str) -> dict:
        ''' Using the emulate function to replay the tx softly (for debug) '''
        pass

    def emulate_tx_body(self, wallet: Wallet, tx_body: dict, block:str = "best"):
        '''
        Emulate execution of a transaction

        The response json structure please view README.md
        '''
        emulate_body = copy.deepcopy(tx_body)
        emulate_body['caller'] = wallet.getAddress()
        del emulate_body["chainTag"]
        del emulate_body["gasPriceCoef"]
        del emulate_body["dependsOn"]
        del emulate_body["nonce"]
        url = build_url(self.url, f'/accounts/*')
        r = requests.post(url, headers={'accept': 'application/json','Content-Type': 'application/json'}, json=emulate_body)
        if not (r.status_code == 200):
            raise Exception(f"HTTP error: {r.status_code} {r.text}")

        return r.json()

    def build_tx_body(self, wallet: Wallet, to, value, data, gas:int=None, dependsOn=None) -> dict:
        block = self.get_block('best')
        blockRef = calc_blockRef(block['id'])
        nonce = calc_nonce()
        chainTag = self.get_chainTag()
        body = {
            "chainTag": chainTag,
            "blockRef": blockRef,
            "expiration": 32,
            "clauses": [
                {
                    "to": to,
                    "value": value,
                    "data": data
                }
            ],
            "gasPriceCoef": 0,
            # "gas": gas,
            "dependsOn": dependsOn,
            "nonce": nonce
        }

        responses = self.emulate_tx_body(wallet, body)
        if is_emulate_failed(responses):
            raise Exception(f'Emulation failed: {responses}')
        
        gases = read_vm_gases(responses)
        if gas and gas < gases[0]:
            raise Exception(f'gas {gas} < emulated vm gas result {gases[0]}')
        
        body['gas'] = 0
        tx = transaction.Transaction(body)
        intrinsic_gas = tx.get_intrinsic_gas()
        
        if gas:
            body['gas'] = gas + intrinsic_gas + 15000
        else:
            body['gas'] = gases[0] + intrinsic_gas + 15000

        return body

    def build_tx_unsigned(self, tx_body: dict, encode=False) -> Union[transaction.Transaction, str]:
        tx = transaction.Transaction(tx_body)
        if encode:
            return '0x' + tx.encode().hex()
        else:
            return tx

    def build_tx_signed(self, wallet: Wallet, tx_body: dict, encode=False) -> Union[transaction.Transaction, str]:
        tx = self.build_tx_unsigned(tx_body)
        message_hash = tx.get_signing_hash()
        signature = wallet.sign(message_hash)
        tx.set_signature(signature)
        if encode:
            return '0x' + tx.encode().hex()
        else:
            return tx
