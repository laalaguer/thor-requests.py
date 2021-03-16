VeChain Thor for humans.

```python
from thor_requests import Connect, Wallet, Contract, Function, Manager

# chaintag can be derived from block_0
connector = Connect(url='')

wallet = Wallet.fromPrivate(private=b'')
wallet = Wallet.fromKeyStore(file_path='', k_json='')
wallet = Wallet.fromMnemonic(words=[])
wallet.sign()

contract = Contract(meta_json='', meta_file_path='')
function = Function(abi_json='')

manager = Mananger()

manager.call(connector, wallet, contract, method_name, method_params)
manager.call(connector, wallet, function, function_params)
manager.deploy(connector, wallet, byte_code='')
manager.estimate()
```