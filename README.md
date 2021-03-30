VeChain for humans.

This library enables you to talk to VeChain blockchain without hassle.

## Installation

```
pip3 install -U thor-requests
```

# Tutorials

## Pure Information Fetch
```python
from thor_requests.connect import Connect

c = Connect("http://testnet.veblocks.net")

# Fetch an account
res = c.get_account('0x7567d83b7b8d80addcb281a71d54fc7b3364ffed')
print(res)

# Fetch a block
res = c.get_block('0x6ba6507f002f38a8cb32178d8c5189a4e6c223229bb20bb5fd78e3fb526737ba')
print(res)

# Fetch a tx
res = c.get_tx("0xda2ce6bddfb3bd32541c999e81ef56019a6314a23c90a466896aeefca33aebc1")
print(res)

# Fetch a tx receipt
res = c.get_tx_receipt('0xda2ce6bddfb3bd32541c999e81ef56019a6314a23c90a466896aeefca33aebc1')
print(res)

# Fetch what the chainTag this chain is
res = c.get_chainTag()
print(res)
```
## Debug a Failed Tx
```python
from thor_requests.connect import Connect

c = Connect("http://testnet.veblocks.net")
# Replay a known tx (usually failed), get revert reason
# This will get you detailed debug information
res = c.replay_tx("0x1d05a502db56ba46ccd258a5696b9b78cd83de6d0d67f22b297f37e710a72bb5")
print(res)
```

## Call a Smart Contract Function (won't spend gas, just emulate)

## Execute a Smart Contract Function (spend gas)

## Deploy a Smart Contract