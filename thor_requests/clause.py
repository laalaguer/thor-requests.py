'''
    Clause is a unique feature in VeChain Thor.
    While Ethereum is a single clause transaction, (single-clause-tx)
    VeChain can have multiple-clause tx.
'''

from typing import List
from thor_requests.contract import Contract


class Clause:
    def __init__(self, to: str, contract: Contract=None, func_name: str=None, func_params: List=None, value: int=0):
        '''
        There are two types of clause:

        1) "Call": function call to a smart contract
        Build a clause according to the function name and params.
        raise Exception when function is not found by name.

        2) "Pure": only transfer of VET:
        Set the contract, func_name, and func_params to None

        Parameters
        ----------
        to : str
            Address of the contract or receiver account.
        contract : Contract
            To which contract this function belongs.
        func_name : str, optional
            Name of the function.
        func_params : List, optional
            Function params supplied by user.
        value : int, optional
            VET sent with the clause in Wei, by default 0
        '''
        # input
        self.contract = contract
        self.func_name = func_name
        self.func_params = func_params
        self.value = value

        self.is_call = contract and func_name
        if self.is_call:  # Contract call
            f = contract.get_function_by_name(func_name, strict_mode=True)
            data = f.encode(func_params, to_hex=True)
            self.dict = {"to": to, "value": str(value), "data": data}
        else:  # VET transfer
            self.dict = {"to": to, "value": str(value), "data": "0x"}
    
    def is_call(self) -> bool:
        '''
        If is a smart contract call

        Returns
        -------
        bool
            True: is, False: is not
        '''
        return self.is_call

    def get_func_name(self) -> str:
        return self.func_name
    
    def get_contract(self) -> Contract:
        return self.contract

    def to_dict(self) -> dict:
        '''
        Export clause as a dict.

        Returns
        -------
        dict
            The clause as a dict: {"to":, "value":, "data":}
        '''
        return self.dict