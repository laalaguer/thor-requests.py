from .fixtures import solo_connector

def test_ticker(solo_connector):
    block_numbers = []
    for block in solo_connector.ticker():
        block_numbers.append(int(block['number']))
        if len(block_numbers) > 3:
            break;
    
    assert sorted(block_numbers) == block_numbers