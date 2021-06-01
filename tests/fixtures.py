import pytest
from thor_requests.wallet import Wallet
from thor_requests.connect import Connect
from thor_requests.contract import Contract


@pytest.fixture
def vtho_contract_address():
    return "0x0000000000000000000000000000456e65726779"


@pytest.fixture
def solo_connector():
    return Connect("http://localhost:8669")


@pytest.fixture
def solo_wallet():
    return Wallet.fromMnemonic(
        [
            "denial",
            "kitchen",
            "pet",
            "squirrel",
            "other",
            "broom",
            "bar",
            "gas",
            "better",
            "priority",
            "spoil",
            "cross",
        ]
    )


@pytest.fixture
def testnet_connector():
    return Connect("http://testnet.veblocks.net")


@pytest.fixture
def testnet_wallet():
    return Wallet.fromPrivateKey(
        bytes.fromhex(
            "dce1443bd2ef0c2631adc1c67e5c93f13dc23a41c18b536effbbdcbcdb96fb65"
        )
    )


@pytest.fixture
def clean_wallet():
    return Wallet.newWallet()


@pytest.fixture
def vvet_contract():
    return Contract.fromFile("tests/VVET9.json")


@pytest.fixture
def vtho_contract():
    return Contract.fromFile("tests/VTHO.json")
