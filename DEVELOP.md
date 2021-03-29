```python
from thor_requests import Connect, Wallet, Contract

wallet = Wallet.fromPrivate(private=b'')
wallet = Wallet.fromKeyStore(k_json='')
wallet = Wallet.fromMnemonic(words=[])

contract = Contract(meta_dict='')
contract = Contract.fromFile(meta_file='')

# chaintag can be derived from block_0
connector = Connect(url='')
connector.get_account(address='')
connector.get_chain_tag()
connector.get_block(revision='best')
connector.get_block_ref()
connector.get_tx_receipt(tx_id='')
connector.wait_for_tx_receipt(tx_id='')
connector.replay_tx(tx_id='')
connector.call(wallet, contract, method_name, method_params, to, value=0, gas=None)
connector.commit(wallet, contract, method_name, method_params, to, value=0, gas=None)
connector.deploy(wallet, contract)
```