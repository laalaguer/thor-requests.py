""" Contract is a representation of an underlying Solidity compiled JSON """
from typing import Union, List
from .utils import read_json_file


class Contract:
    def __init__(self, meta_dict: dict):
        self.contract_meta: dict = meta_dict

    @classmethod
    def fromFile(cls, path_or_str):
        meta_dict = read_json_file(path_or_str)
        return cls(meta_dict)

    def get_bytecode(self, key: str = "bytecode") -> bytes:
        """ Get bytecode """
        return bytes.fromhex(self.contract_meta[key])

    def get_abi(self, func_name: str) -> Union[dict, None]:
        """ Get specific ABI by function name, or None if not found """
        abis = self.contract_meta["abi"]
        targets = [each for each in abis if each.get("name") == func_name]
        assert len(targets) <= 1  # Zero or at most, one found.
        if len(targets):
            return targets[0]
        else:
            return None

    def get_abis(self) -> List:
        """ Get ABIs of this contract as a list """
        return self.contract_meta["abi"]
