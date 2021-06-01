# These test are integration tests.
# Test the workflow of deploy, emulate call and transact call.

import pytest

from .fixtures import solo_connector, solo_wallet, vvet_contract
from thor_requests import utils


@pytest.fixture(autouse=True)
def deploy_vvet(solo_connector, solo_wallet, vvet_contract):
    """Deploy a smart contract that has no params in constructor"""
    res = solo_connector.deploy(solo_wallet, vvet_contract, None, None, 0)
    assert "id" in res  # Should contain a {'id': '0x...' }
    # print(f"deploy_vvet_tx_id: {res['id']}")
    tx_id = res["id"]
    # Should have the deployed contract address now
    receipt = solo_connector.wait_for_tx_receipt(tx_id)
    created_contracts = utils.read_created_contracts(receipt)
    assert len(created_contracts) == 1
    # print(f"created_vvet_address: {created_contracts[0]}")
    return created_contracts[0]


def test_call(deploy_vvet, solo_connector, solo_wallet, vvet_contract):
    """Emulate call 'balanceOf()' function"""
    vvet_contract_addr = deploy_vvet
    res = solo_connector.call(
        solo_wallet.getAddress(),
        vvet_contract,
        "balanceOf",
        [solo_wallet.getAddress()],
        vvet_contract_addr,
    )
    assert res["decoded"]["0"] == 0  # balanceOf() newly created contract shall be zero


def test_transact(deploy_vvet, solo_connector, solo_wallet, vvet_contract):
    """Real call of the 'balanceOf()' function using transact()"""
    vvet_contract_addr = deploy_vvet
    # Try to emulate the deposite() first,
    # Which will return the events along with the call.
    res = solo_connector.call(
        solo_wallet.getAddress(),
        vvet_contract,
        "deposit",
        [],
        vvet_contract_addr,
        value=3 * (10 ** 18),  # 3 vet
    )
    assert res["reverted"] == False
    assert res["events"][0]["decoded"]["wad"] == 3 * (10 ** 18)

    balance_1 = int(solo_connector.get_account(solo_wallet.getAddress())["balance"], 16)

    # Then we do the real call of deposit()
    res = solo_connector.transact(
        solo_wallet,
        vvet_contract,
        "deposit",
        [],
        vvet_contract_addr,
        value=3 * (10 ** 18),  # 3 vet
    )
    assert res["id"]

    tx_id = res["id"]
    receipt = solo_connector.wait_for_tx_receipt(tx_id)

    balance_2 = int(solo_connector.get_account(solo_wallet.getAddress())["balance"], 16)
    assert balance_1 - balance_2 == 3 * (10 ** 18)
