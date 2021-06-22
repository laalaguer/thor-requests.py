""" Test VET transfer """
from .fixtures import (
    solo_connector,
    solo_wallet,
    clean_wallet,
)


def test_vet_transfer(solo_connector, solo_wallet, clean_wallet):
    sender = solo_wallet.getAddress()
    receiver = clean_wallet.getAddress()

    sender_vet = solo_connector.get_vet_balance(sender)
    sender_vtho = solo_connector.get_vtho_balance(sender)
    # print(f"sender: vet {sender_vet}, vtho {sender_vtho}")

    receiver_vet = solo_connector.get_vet_balance(receiver)
    receiver_vtho = solo_connector.get_vtho_balance(receiver)
    # print(f"receiver: vet {receiver_vet}, vtho {receiver_vtho}")

    res = solo_connector.transfer_vet(solo_wallet, receiver, 3 * (10 ** 18))  # 3 vet
    assert res["id"]
    tx_id = res["id"]
    receipt = solo_connector.wait_for_tx_receipt(tx_id)

    receiver_vet_2 = solo_connector.get_vet_balance(receiver)
    assert (receiver_vet_2 - receiver_vet) == 3 * (10 ** 18)
