VeChain for humans.

This library enables you to talk to VeChain blockchain without hassle.

## Install

```
pip3 install -U thor-requests
```

## Local Development

```bash
# Local dependencies
$ make install
```

## Examples

**Debug a known transaction**

```python
# activate environment & run exmample
from thor_requests.connect import Connect

c = Connect("http://testnet.veblocks.net")
response = c.replay_tx("0x1d05a502db56ba46ccd258a5696b9b78cd83de6d0d67f22b297f37e710a72bb5")
print(response)
```
