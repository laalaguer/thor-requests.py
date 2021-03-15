VeChain Thor for humans.

```python
from thor_requests import Connect, Wallet, Contract, Function, Manager

connector = Connect(url='', chaintag='')
wallet = Wallet(priv='', keystore='', password='', words='')

contract = Contract(meta='')
function = Function(abi={})

manager = Mananger()

manager.call(connector, wallet: optional, contract, method_name, method_params)
manager.call(connector, wallet: optional, function, function_params)
manager.estimate()
```