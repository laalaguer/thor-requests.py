from thor_requests.connect import Connect

c = Connect("http://testnet.veblocks.net")
print(c.replay_tx("0xb4f7e9d13cca5eb9390de9a46290b390275bfad1082ba0ddb09b9806a4cd0fe2"))
