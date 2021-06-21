""" Test if the timeout works """
import pytest
from .fixtures import solo_connector
import requests


def test_short_timeout(solo_connector):
    solo_connector.set_timeout(0.001)  # extreme short timeout
    if solo_connector.get_endpoint() == 'http://localhost:8669':
        # Timeout won't work on local, the response is super fast
        # So we jump over the test when testing local
        return
    else:
        # Should Throw
        with pytest.raises(requests.exceptions.ReadTimeout):
            res = solo_connector.get_block()
