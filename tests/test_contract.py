# Focus on smart contract.
from thor_requests.contract import Contract


def test_name():
    """Get name from smart contracts"""

    # New style compiled json
    contract_1 = Contract.fromFile("tests/UniswapV2Pair.json")
    assert contract_1.get_contract_name() == "UniswapV2Pair"

    # Old style compiled json
    contract_2 = Contract.fromFile("tests/VVET9.json")
    assert contract_2.get_contract_name() == "VVET9"
