''' Test the Fee Delegation feature via VET and VTHO transfer '''

from .fixtures import (
    solo_connector,
    solo_wallet,
    clean_wallet,
    vtho_contract_address,
    vtho_contract,
)
from thor_requests import utils
from thor_devkit import transaction


def test_vet_transfer(solo_connector, solo_wallet, clean_wallet):
    sender = solo_wallet.getAddress()
    receiver = clean_wallet.getAddress()

    sender_vet = solo_connector.get_vet_balance(sender)
    sender_vtho = solo_connector.get_vtho_balance(sender)
    # print(f"sender: vet {sender_vet}, vtho {sender_vtho}")

    receiver_vet = solo_connector.get_vet_balance(receiver)
    receiver_vtho = solo_connector.get_vtho_balance(receiver)
    # print(f"receiver: vet {receiver_vet}, vtho {receiver_vtho}")

    res = solo_connector.transfer_vet(
        solo_wallet,
        receiver,
        3 * (10 ** 18)
    )  # 3 vet
    assert res["id"]
    tx_id = res["id"]
    receipt = solo_connector.wait_for_tx_receipt(tx_id)

    receiver_vet_2 = solo_connector.get_vet_balance(receiver)
    assert (receiver_vet_2 - receiver_vet) == 3 * (10 ** 18)

    # Clean wallet transfer VET back to solo (use fee delegation feature)
    res = solo_connector.transfer_vet(
        clean_wallet,
        sender,
        3 * (10 ** 18),
        solo_wallet
    )
    assert res["id"]
    tx_id = res["id"]
    receipt = solo_connector.wait_for_tx_receipt(tx_id)

    receiver_vet_3 = solo_connector.get_vet_balance(receiver)
    assert receiver_vet_3 == 0


"""Test of transferring vtho between accounts"""


def test_transfer_vtho_easy(
    solo_connector,
    solo_wallet,
    clean_wallet
):
    # Check the sender's vtho balance
    sender_balance = solo_connector.get_vtho_balance(solo_wallet.getAddress())
    assert sender_balance > 0

    # Check the receiver's vtho balance
    receiver_balance = solo_connector.get_vtho_balance(
        clean_wallet.getAddress()
    )
    assert receiver_balance == 0

    # Do the vtho transfer from sender to receiver
    res = solo_connector.transfer_vtho(
        solo_wallet,
        clean_wallet.getAddress(),
        3 * (10 ** 18)
    )
    tx_id = res["id"]
    receipt = solo_connector.wait_for_tx_receipt(tx_id)

    # Check the receiver's vtho balance
    updated_balance = solo_connector.get_vtho_balance(
        clean_wallet.getAddress()
    )
    assert updated_balance == 3 * (10 ** 18)

    # Receiver transfer VTHO back to sender (using fee delegation feature)
    res = solo_connector.transfer_vtho(
        clean_wallet,
        solo_wallet.getAddress(),
        3 * (10 ** 18),
        solo_wallet
    )
    tx_id = res["id"]
    receipt = solo_connector.wait_for_tx_receipt(tx_id)

    # Check the receiver's vtho balance
    updated_balance = solo_connector.get_vtho_balance(
        clean_wallet.getAddress()
    )
    assert updated_balance == 0


def test_sign_fee_delegation_allow(
    solo_wallet,
    clean_wallet
):
    delegated_body = {
        "chainTag": 1,
        "blockRef": "0x00000000aabbccdd",
        "expiration": 32,
        "clauses": [
            {
                "to": "0x7567d83b7b8d80addcb281a71d54fc7b3364ffed",
                "value": 10000,
                "data": "0x000000606060"
            }
        ],
        "gasPriceCoef": 128,
        "gas": 21000,
        "dependsOn": None,
        "nonce": 12345678,
        "reserved": {
            "features": 1
        }
    }

    delegated_tx = transaction.Transaction(delegated_body)
    raw_tx = '0x' + delegated_tx.encode().hex()

    def allPass(tx_payer:str, tx_origin:str, txObj:transaction.Transaction):
        ''' Blindly allow the tx to pass '''
        return True, ''
    
    result = utils.sign_delegated_tx(solo_wallet, clean_wallet.getAddress(), raw_tx, False, allPass)
    assert len(result['signature']) > 0
    assert len(result['error_message']) == 0


def test_sign_fee_delegation_reject(
    solo_wallet,
    clean_wallet
):
    ''' Reject the tx sign '''
    delegated_body = {
        "chainTag": 1,
        "blockRef": "0x00000000aabbccdd",
        "expiration": 32,
        "clauses": [
            {
                "to": "0x7567d83b7b8d80addcb281a71d54fc7b3364ffed",
                "value": 10000,
                "data": "0x000000606060"
            }
        ],
        "gasPriceCoef": 128,
        "gas": 21000,
        "dependsOn": None,
        "nonce": 12345678,
        "reserved": {
            "features": 1
        }
    }

    delegated_tx = transaction.Transaction(delegated_body)
    raw_tx = '0x' + delegated_tx.encode().hex()

    def allPass(tx_payer:str, tx_origin:str, txObj:transaction.Transaction):
        return False, 'I just dont allow this tx to pass'
    
    result = utils.sign_delegated_tx(solo_wallet, clean_wallet.getAddress(), raw_tx, False, allPass)
    assert len(result['signature']) == 0
    assert result['error_message'] == 'I just dont allow this tx to pass'


def test_sign_if_emulate_success(
    solo_connector,
    solo_wallet,
    clean_wallet,
    vtho_contract_address,
    vtho_contract
):
    # First, solo wallet send 3 vtho to the clean wallet
    res = solo_connector.transfer_vtho(solo_wallet, clean_wallet.getAddress(), 3 * 10 ** 18)
    tx_id = res["id"]
    receipt = solo_connector.wait_for_tx_receipt(tx_id)
    assert utils.is_reverted(receipt) == False

    # Then, construct a tx which sends back 3 vtho to solo wallet,
    # But tx is sponsored by the solo wallet
    chainTag = solo_connector.get_chainTag()
    best_block = solo_connector.get_block("best")
    blockRef = utils.calc_blockRef(best_block["id"])
    nonce = utils.calc_nonce()

    clause = solo_connector.clause(vtho_contract, 'transfer', [solo_wallet.getAddress(), 3 * 10 ** 18], vtho_contract_address)
    delegated_body = utils.build_tx_body(
        [clause.to_dict()],
        chainTag,
        blockRef,
        nonce,
        gas=100000,
        feeDelegation=True
    )

    delegated_tx = transaction.Transaction(delegated_body)
    raw_tx = '0x' + delegated_tx.encode().hex()

    def emulate_then_judge(tx_payer:str, tx_origin:str, txObj:transaction.Transaction):
        ''' If emulation failed then refuse to sign the transaction '''
        old_body = txObj.get_body()
        e_responses = solo_connector.emulate_tx(tx_origin, old_body, gas_payer=tx_payer)
        if utils.any_emulate_failed(e_responses):
            return False, 'Emulation failed'
        return True, ''
    
    # Ask for gas payer's signature
    result = utils.sign_delegated_tx(solo_wallet, clean_wallet.getAddress(), raw_tx, False, emulate_then_judge)
    assert len(result['signature']) > 0
    assert len(result['error_message']) == 0

    # Assemble tx
    user_signagure = clean_wallet.sign(delegated_tx.get_signing_hash())
    server_signature = bytes.fromhex(result['signature'].lstrip('0x'))

    sig = user_signagure + server_signature

    delegated_tx.set_signature(sig)
    assert delegated_tx.is_delegated() == True

    assert delegated_tx.get_origin() == clean_wallet.getAddress()
    assert delegated_tx.get_delegator() == solo_wallet.getAddress()

    # Post tx （and should success)
    raw_tx_again = "0x" + delegated_tx.encode().hex()
    res = solo_connector.post_tx(raw_tx_again)
    tx_id = res['id']
    receipt = solo_connector.wait_for_tx_receipt(tx_id)
    assert utils.is_reverted(receipt) == False