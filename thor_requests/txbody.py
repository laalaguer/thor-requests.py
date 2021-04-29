from .connect import Connect


class TxBody:
    """ Tx body """

    def __init__(self, connector: Connect):
        self.c = connector

    def set_blockRef(blockRef: str = None):
        ''' Set blockRef to txbody '''
        pass

    def set_nonce(nonce: int = None):
        ''' Set nonce to tx body '''
        pass

    def set_gas(gas: int = None):
        ''' Set gas to tx body '''
        pass

    def add_clause(self, to, value, data):
        ''' Add a clause to tx body '''
        pass

    def format() -> dict:
        '''
        Output TxBody as dict.

        Note:
            If nonce is not set, will get a random
            If gas is not set, will be 0
        '''
        pass