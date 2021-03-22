from thor_requests import connect
from thor_requests import wallet

w = wallet.Wallet.fromPrivateKey(bytes.fromhex('dce1443bd2ef0c2631adc1c67e5c93f13dc23a41c18b536effbbdcbcdb96fb65'))
c = connect.Connect('http://solo.veblocks.net')
tx_body = {
  "clauses": [
    {
      "to": "0x5034aa590125b64023a0262112b98d72e3c8e40e",
      "value": "0xde0b6b3a7640000",
      "data": "0x5665436861696e2054686f72"
    }
  ],
  "gas": 1,
  "gasPrice": "1000000000000000",
  "caller": "0x7567d83b7b8d80addcb281a71d54fc7b3364ffed",
  "provedWork": "1000",
  "gasPayer": "0xd3ae78222beadb038203be21ed5ce7c9b1bff602",
  "expiration": 1000,
  "blockRef": "0x00000000851caf3c"
}

print(c.build_tx_body(w, "0x5034aa590125b64023a0262112b98d72e3c8e40e", "0xde0b6b3a7640000", "0x5665436861696e2054686f72"))