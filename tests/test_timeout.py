""" Test if the timeout works """
import pytest
from .fixtures import solo_connector
import requests


def test_short_timeout(solo_connector):
    solo_connector.set_timeout(0.001)  # extreme short timeout
    # Should Throw
    with pytest.raises(requests.exceptions.ReadTimeout):
        res = solo_connector.get_block()
