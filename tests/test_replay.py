import pytest

from .fixtures import testnet_connector


def test_replay(testnet_connector):
    """A known failed test on testnet which has revert reason"""
    res = testnet_connector.replay_tx(
        "0x1d05a502db56ba46ccd258a5696b9b78cd83de6d0d67f22b297f37e710a72bb5"
    )
    assert "decoded" in res[0]
    assert "revertReason" in res[0]["decoded"]
    assert res[0]["decoded"]["revertReason"] == "transfer to the zero address"
