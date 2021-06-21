from thor_devkit import cry
from thor_devkit.cry import mnemonic, keystore, secp256k1


def check(priv: bytes):
    '''Check private key format, or raise exception'''
    if len(priv) != 32:
        raise Exception("Private key should be 32 bytes")


class Wallet:
    def __init__(self, priv: bytes):
        check(priv)
        self.priv: bytes = priv
        self.public: bytes = secp256k1.derive_publicKey(self.priv)
        self.address_bytes: bytes = cry.public_key_to_address(self.public)
        self.address: str = "0x" + self.address_bytes.hex()

    @classmethod
    def fromPrivateKey(cls, priv: bytes):
        """Get a wallet from private key"""
        return cls(priv)

    @classmethod
    def fromMnemonic(cls, words: list):
        """Get a wallet from words"""
        if not mnemonic.validate(words):
            raise Exception("Words validation failed, check spelling?")
        priv = mnemonic.derive_private_key(words)
        return cls(priv)

    @classmethod
    def fromKeyStore(cls, ks: dict, password: bytes):
        """Get a wallet from keystore (dict)"""
        if not keystore.well_formed(ks):
            raise Exception("Keystore is not well formed")

        priv = keystore.decrypt(ks, password)
        return cls(priv)

    @classmethod
    def newWallet(cls):
        """Get a plain new random wallet"""
        private_key = secp256k1.generate_privateKey()
        return cls(private_key)

    def sign(self, msg_hash: bytes) -> bytes:
        """Sign the stuff with this wallet"""
        signature = secp256k1.sign(msg_hash, self.priv)
        return signature

    def verifySignature(self, msg_hash: bytes, signature: bytes) -> bool:
        """Verify signature if signed by us."""
        public_key = secp256k1.recover(msg_hash, signature)
        return public_key == self.public

    def getAddress(self) -> str:
        '''Get string reprensentation of the wallet address'''
        return self.address
