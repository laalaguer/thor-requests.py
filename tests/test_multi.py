from .fixtures import (
    solo_connector,
    solo_wallet,
    clean_wallet,
    vtho_contract,
    vtho_contract_address,
)


def test_multi_vtho(
    solo_connector, solo_wallet, clean_wallet, vtho_contract, vtho_contract_address
):
    c1 = solo_connector.clause(
        vtho_contract,
        "transfer",
        [clean_wallet.getAddress(), 1 * (10 ** 18)],  # 1 vtho
        vtho_contract_address,
    )

    c2 = solo_connector.clause(
        vtho_contract,
        "transfer",
        [clean_wallet.getAddress(), 2 * (10 ** 18)],  # 2 vtho
        vtho_contract_address,
    )

    responses = solo_connector.call_multi(
        solo_wallet.getAddress(),
        clauses=[c1, c2],
    )

    for each in responses:
        assert each["reverted"] == False
