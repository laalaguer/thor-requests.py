# Deploy a smart contract and call the function,
# to trigger a reverted transaction.
# Then validate the revert reason via replay.
import pytest
from thor_requests import utils

from .fixtures import (
    testnet_connector,
    solo_connector,
    solo_wallet,
    checknumber_contract,
)

# def test_replay(testnet_connector):
#     """A known failed test on testnet which has revert reason"""
#     res = testnet_connector.replay_tx(
#         "0x1d05a502db56ba46ccd258a5696b9b78cd83de6d0d67f22b297f37e710a72bb5"
#     )
#     assert "decoded" in res[0]
#     assert "revertReason" in res[0]["decoded"]
#     assert res[0]["decoded"]["revertReason"] == "transfer to the zero address"


@pytest.fixture(autouse=True)
def deploy_checknumber(solo_connector, solo_wallet, checknumber_contract):
    """Deploy a solo contract before we do any test"""
    res = solo_connector.deploy(solo_wallet, checknumber_contract, None, None, 0)
    assert "id" in res
    tx_id = res["id"]
    # Should have the deployed contract address now
    receipt = solo_connector.wait_for_tx_receipt(tx_id)
    created_contracts = utils.read_created_contracts(receipt)
    assert len(created_contracts) == 1
    # print(f"created_vvet_address: {created_contracts[0]}")
    return created_contracts[0]


def test_call_with_revert(
    deploy_checknumber, solo_connector, solo_wallet, checknumber_contract
):
    """Test if the emulation is failed, should revert reason be shown?"""
    contract_addr = deploy_checknumber
    res = solo_connector.call(
        solo_wallet.getAddress(),
        checknumber_contract,
        "greaterThan10",
        [8],  # 8 is less than 10
        contract_addr,
    )
    assert res["decoded"]["revertReason"] == "Size shall be greater than 10"


def test_transact_then_replay(
    deploy_checknumber, solo_connector, solo_wallet, checknumber_contract
):
    """If the tx is reverted, should revert reason be shown?"""
    contract_addr = deploy_checknumber
    res = solo_connector.transact(
        solo_wallet,
        checknumber_contract,
        "greaterThan10",
        [8],  # 8 is less than 10
        contract_addr,
        value=0,
        force=True,  # force execute the tx (normally it will fail)
    )
    assert res["id"]
    tx_id = res["id"]

    # Wait for the reverted tx to be packed into blockchain
    receipt = solo_connector.wait_for_tx_receipt(tx_id)
    res = solo_connector.replay_tx(tx_id)

    # Replay the tx!
    assert res[0]["decoded"]["revertReason"] == "Size shall be greater than 10"
