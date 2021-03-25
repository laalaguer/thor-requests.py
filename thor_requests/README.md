## Emulate Response (Success)
```python
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
```python
[
  {
    "data": "0x", # if we have data here then it is Error(string) type of data
    "events": [],
    "transfers": [],
    "gasUsed": 0,
    "reverted": true,
    "vmError": "insufficient balance for transfer"
  }
]
```