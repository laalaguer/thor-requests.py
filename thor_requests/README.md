## Emulate Response (Success)
```javascript
[
  {
    "data": "0x103556a73c10e38ffe2fc4aa50fc9d46ad0148f07e26417e117bd1ece9d948b5",
    "events": [
      {
        "address": "0x7567d83b7b8d80addcb281a71d54fc7b3364ffed",
        "topics": [
          "0x4de71f2d588aa8a1ea00fe8312d92966da424d9939a511fc0be81e65fad52af8"
        ],
        "data": "0x4de71f2d588aa8a1ea00fe8312d92966da424d9939a511fc0be81e65fad52af8"
      }
    ],
    "transfers": [
      {
        "sender": "0xdb4027477b2a8fe4c83c6dafe7f86678bb1b8a8d",
        "recipient": "0x5034aa590125b64023a0262112b98d72e3c8e40e",
        "amount": "0x47fdb3c3f456c0000"
      }
    ],
    "gasUsed": 21000,
    "reverted": false,
    "vmError": ""
  }
]
```

## Emulate Response (Failure)
```javascript
[
  {
    "data": "0x", // if we have data here then it is Error(string) type of data
    "events": [],
    "transfers": [],
    "gasUsed": 0,
    "reverted": true,
    "vmError": "insufficient balance for transfer"
  }
]
```

## Get Receipt Response (Success)
```javascript
{
  "gasUsed": 21000,
  "gasPayer": "0xdb4027477b2a8fe4c83c6dafe7f86678bb1b8a8d",
  "paid": "0x1236efcbcbb340000",
  "reward": "0x576e189f04f60000",
  "reverted": false,
  "outputs": [
    {
      "contractAddress": null,
      "events": [
        {
          "address": "0x7567d83b7b8d80addcb281a71d54fc7b3364ffed",
          "topics": [
            "0x4de71f2d588aa8a1ea00fe8312d92966da424d9939a511fc0be81e65fad52af8"
          ],
          "data": "0x4de71f2d588aa8a1ea00fe8312d92966da424d9939a511fc0be81e65fad52af8"
        }
      ],
      "transfers": [
        {
          "sender": "0xdb4027477b2a8fe4c83c6dafe7f86678bb1b8a8d",
          "recipient": "0x5034aa590125b64023a0262112b98d72e3c8e40e",
          "amount": "0x47fdb3c3f456c0000"
        }
      ]
    }
  ],
  "meta": {
    "blockID": "0x0004f6cc88bb4626a92907718e82f255b8fa511453a78e8797eb8cea3393b215",
    "blockNumber": 325324,
    "blockTimestamp": 1533267900,
    "txID": "0x284bba50ef777889ff1a367ed0b38d5e5626714477c40de38d71cedd6f9fa477",
    "txOrigin": "0xdb4027477b2a8fe4c83c6dafe7f86678bb1b8a8d"
  }
}
```

## Get Receipt Response (Failure)
```javascript
{
  "gasUsed": 22315,
  "gasPayer": "0x7567d83b7b8d80addcb281a71d54fc7b3364ffed",
  "paid": "0x1d121a841b0d10eff",
  "reward": "0x8b8a18e081d8514c",
  "reverted": true,
  "meta": {
    "blockID": "0x0078542c5558a50b5e71ca8464755eb7a9e7772dea770ef71b7b3038a0b83ec9",
    "blockNumber": 7885868,
    "blockTimestamp": 1608889850,
    "txID": "0x1d05a502db56ba46ccd258a5696b9b78cd83de6d0d67f22b297f37e710a72bb5",
    "txOrigin": "0x7567d83b7b8d80addcb281a71d54fc7b3364ffed"
  },
  "outputs": []
}
```

## Post tx (success)
```javascript
{'id': '0xd49b857824a266c0768a4699b6693347cc9f3fb287a62fa574dab18a60db0ece'}
```