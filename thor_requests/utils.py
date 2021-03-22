from typing import List
import json
from os import EX_CANTCREAT
import secrets
from thor_devkit import abi, cry, transaction
from thor_devkit.cry import secp256k1

def build_url(base: str, tail: str) -> str:
    ''' Build a proper URL, base + tail '''
    return base.rstrip('/') + '/' + tail.lstrip('/')


def read_json_file(path_like: str) -> dict:
    ''' Read json file '''
    with open(path_like, 'r') as f:
        return json.load(f)


def build_params(types: list, args: list) -> bytes:
    ''' ABI encode params according to types '''
    return abi.Coder.encode_list(types, args)


def calc_address(priv: bytes) -> str:
    ''' Calculate an address from a given private key '''
    public_key = secp256k1.derive_publicKey(priv)
    _address_bytes = cry.public_key_to_address(public_key)
    address = '0x' + _address_bytes.hex()
    return address


def calc_nonce() -> int:
    ''' Calculate a random number for nonce '''
    return int(secrets.token_hex(8), 16)


def calc_blockRef(block_id: str) -> str:
    ''' Calculate a blockRef from a given block_id, id should starts with 0x'''
    if not block_id.startswith('0x'):
        raise Exception("block_id should start with 0x")
    return block_id[0:18]


def calc_chaintag(hex_str: str) -> int:
    ''' hex_str can be both like '0x4a' or just '4a' '''
    return int(hex_str, 16)


def emulate_failed(emulate_responses: List) -> bool:
    for each_response in emulate_responses:
        if each_response['reverted'] == True:
            return True
    
    return False


def emulated_vm_gases(emulated_responses: List) -> List[int]:
    gasUsed = []
    for each_response in emulated_responses:
        gasUsed.append(int(each_response['gasUsed']))
    
    return gasUsed
