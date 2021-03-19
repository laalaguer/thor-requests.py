VeChain Thor for humans.

```python
from thor_requests import Connect, Wallet, Contract, Function, Manager

wallet = Wallet.fromPrivate(private=b'')
wallet = Wallet.fromKeyStore(k_json='')
wallet = Wallet.fromMnemonic(words=[])

contract = Contract.fromFile(meta_file='')
contract = Contract.fromJson(meta_dict='')

# chaintag can be derived from block_0
connector = Connect(url='')
connector.get_account(address='')
connector.get_chain_tag()
connector.get_block(revision='best')
connector.get_block_ref()
connector.call(wallet, contract, method_name, method_params, to, value=0, gas=None)
connector.emulate(wallet, contract, method_name, method_params, to, value)
connector.deploy(wallet, contract)
```
