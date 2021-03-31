VeChain for humans.

This library enables you to talk to VeChain blockchain without hassle.

## Installation

```
pip3 install -U thor-requests
```

# Tutorials

## Fetch Tx/Block/Account/Receipt
```python
from thor_requests.connect import Connect

c = Connect("http://testnet.veblocks.net")

# Account
c.get_account('0x7567d83b7b8d80addcb281a71d54fc7b3364ffed')

# >>> {'balance': '0x21671d16fd19254d67', 'energy': '0xf809f75231563b5f1d', 'hasCode': False}

# Block
c.get_block('0x0084f21562e046b1ae9aa70b6cd3b7bc2e8312f3961716ee3fcd58ce8bcb7392')

# >>> {'number': 8712725, 'id': '0x0084f21562e046b1ae9aa70b6cd3b7bc2e8312f3961716ee3fcd58ce8bcb7392', 'size': 243, 'parentID': '0x0084f214dd0b96059a142b5ac33668a3bb56245bde62d72a7874dc5a842c89e7', 'timestamp': 1617158500, 'gasLimit': 281323205, 'beneficiary': '0xb4094c25f86d628fdd571afc4077f0d0196afb48', 'gasUsed': 0, 'totalScore': 33966653, 'txsRoot': '0x45b0cfc220ceec5b7c1c62c4d4193d38e4eba48e8815729ce75f9c0ab0e4c1c0', 'txsFeatures': 1, 'stateRoot': '0xfe32d569f127a9a1d6f690bb83dae1c91fee31cac6596ae573ad3fa76c209670', 'receiptsRoot': '0x45b0cfc220ceec5b7c1c62c4d4193d38e4eba48e8815729ce75f9c0ab0e4c1c0', 'signer': '0x39218d415dc252a50823a3f5600226823ba4716e', 'isTrunk': True, 'transactions': []}

# Transaction
c.get_tx("0xda2ce6bddfb3bd32541c999e81ef56019a6314a23c90a466896aeefca33aebc1")

# >>> {'id': '0xda2ce6bddfb3bd32541c999e81ef56019a6314a23c90a466896aeefca33aebc1', 'chainTag': 39, 'blockRef': '0x00825266c5688208', 'expiration': 18, 'clauses': [{'to': '0x0000000000000000000000000000456e65726779', 'value': '0x0', 'data': '0xa9059cbb0000000000000000000000007567d83b7b8d80addcb281a71d54fc7b3364ffed0000000000000000000000000000000000000000000000056bc75e2d63100000'}], 'gasPriceCoef': 0, 'gas': 51582, 'origin': '0xfa6e63168115a9202dcd834f6c20eabf48f18ba7', 'delegator': None, 'nonce': '0x32c31a501fcd9752', 'dependsOn': None, 'size': 190, 'meta': {'blockID': '0x0082526895631e850b6cae1ba0a05deb24b8719b6896b69437cea87ee939bf3d', 'blockNumber': 8540776, 'blockTimestamp': 1615439010}}

# Transaction receipt
c.get_tx_receipt('0xda2ce6bddfb3bd32541c999e81ef56019a6314a23c90a466896aeefca33aebc1')

# >>> {'gasUsed': 36582, 'gasPayer': '0xfa6e63168115a9202dcd834f6c20eabf48f18ba7', 'paid': '0x1fbad5f2e25570000', 'reward': '0x984d9c8dd8008000', 'reverted': False, 'meta': {'blockID': '0x0082526895631e850b6cae1ba0a05deb24b8719b6896b69437cea87ee939bf3d', 'blockNumber': 8540776, 'blockTimestamp': 1615439010, 'txID': '0xda2ce6bddfb3bd32541c999e81ef56019a6314a23c90a466896aeefca33aebc1', 'txOrigin': '0xfa6e63168115a9202dcd834f6c20eabf48f18ba7'}, 'outputs': [{'contractAddress': None, 'events': [{'address': '0x0000000000000000000000000000456e65726779', 'topics': ['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef', '0x000000000000000000000000fa6e63168115a9202dcd834f6c20eabf48f18ba7', '0x0000000000000000000000007567d83b7b8d80addcb281a71d54fc7b3364ffed'], 'data': '0x0000000000000000000000000000000000000000000000056bc75e2d63100000'}], 'transfers': []}]}

# Chain Tag
c.get_chainTag()
# >>> 39
```
## Debug a Failed Transaction
```python
from thor_requests.connect import Connect

c = Connect("http://testnet.veblocks.net")
c.replay_tx("0x1d05a502db56ba46ccd258a5696b9b78cd83de6d0d67f22b297f37e710a72bb5")

# >>> 
[{
    'data': '0x08c379a00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000001c7472616e7366657220746f20746865207a65726f206164647265737300000000',
    'events': [],
    'transfers': [],
    'gasUsed': 659,
    'reverted': True,
    'vmError': 'evm: execution reverted',
    'decoded': {
        'revertReason': 'transfer to the zero address'
    }
}]
```

## Call a Contract Function (won't spend gas, just emulate)

## Execute a Contract Function (spend gas)

## Deploy a Smart Contract