from thor_requests.connect import Connect

c = Connect("http://testnet.veblocks.net")
print(c.replay_tx("0x1d05a502db56ba46ccd258a5696b9b78cd83de6d0d67f22b297f37e710a72bb5"))