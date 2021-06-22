"""Test of transferring vtho between accounts"""

import pytest

from .fixtures import (
    solo_connector,
    solo_wallet,
    clean_wallet,
    vtho_contract_address,
    vtho_contract,
)
from thor_requests import utils

def test_transfer_vtho_easy(
    solo_connector,
    solo_wallet,
    clean_wallet,
    vtho_contract_address,
    vtho_contract
):
    # Check the sender's vtho balance
    sender_balance = solo_connector.get_vtho_balance(solo_wallet.getAddress())
    assert sender_balance > 0

    # Check the receiver's vtho balance
    receiver_balance = solo_connector.get_vtho_balance(clean_wallet.getAddress())
    assert receiver_balance == 0

    # Do the vtho transfer!
    res = solo_connector.transfer_vtho(solo_wallet, clean_wallet.getAddress(), 3 * (10 ** 18))
    tx_id = res["id"]
    receipt = solo_connector.wait_for_tx_receipt(tx_id)

    # Check the receiver's vtho balance
    updated_balance = solo_connector.get_vtho_balance(clean_wallet.getAddress())
    assert updated_balance == 3 * (10 ** 18)


def test_transfer_vtho_hard(
    solo_connector,
    solo_wallet,
    clean_wallet,
    vtho_contract_address,
    vtho_contract
):
    """Transfer vtho from big wallet to a clean wallet, using external assembling style"""
    # Check the sender's vtho balance
    res = solo_connector.call(
        solo_wallet.getAddress(),
        vtho_contract,
        "balanceOf",
        [solo_wallet.getAddress()],
        vtho_contract_address,
        value=0,
    )
    assert res["reverted"] == False
    assert res["decoded"]["balance"] > 0

    # Check the receiver's vtho balance
    res = solo_connector.call(
        clean_wallet.getAddress(),
        vtho_contract,
        "balanceOf",
        [clean_wallet.getAddress()],
        vtho_contract_address,
        value=0,
    )
    assert res["reverted"] == False
    assert res["decoded"]["balance"] == 0

    # Do the vtho transfer!
    res = solo_connector.transact(
        solo_wallet,
        vtho_contract,
        "transfer",
        [clean_wallet.getAddress(), 3 * (10 ** 18)],  # transfer 3 vtho
        vtho_contract_address,
        value=0,
    )

    tx_id = res["id"]
    receipt = solo_connector.wait_for_tx_receipt(tx_id)

    # Check the receiver's vtho balance
    res = solo_connector.call(
        clean_wallet.getAddress(),
        vtho_contract,
        "balanceOf",
        [clean_wallet.getAddress()],
        vtho_contract_address,
        value=0,
    )
    assert res["reverted"] == False
    updated_balance = res["decoded"]["balance"]
    assert updated_balance == 3 * (10 ** 18)
