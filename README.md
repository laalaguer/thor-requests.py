VeChain Thor for humans.

```python
from thor_requests import Connect, Wallet, Contract, Function, Manager

wallet = Wallet.fromPrivate(private=b'')
wallet = Wallet.fromKeyStore(file_path='', k_json='')
wallet = Wallet.fromMnemonic(words=[])

contract = Contract(meta_json='', meta_file_path='')

# chaintag can be derived from block_0
connector = Connect(url='')
connector.get_account(address='')
connector.get_chain_tag()
connector.get_block(revision='best')
connector.get_block_ref()
connector.call(wallet, contract, method_name, method_params, to, value=0, gas=None)
connector.emulate()
connector.deploy(wallet, contract)
```
