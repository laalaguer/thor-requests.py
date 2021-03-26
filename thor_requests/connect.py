from typing import Union, List
import requests
from .utils import (
    build_tx_body,
    build_url,
    calc_blockRef,
    calc_chaintag,
    calc_emulate_tx_body,
    calc_nonce,
    any_emulate_failed,
    calc_revertReason,
    is_readonly,
    read_vm_gases,
)
from .wallet import Wallet
from .contract import Contract
from thor_devkit import abi, cry, transaction


class Connect:
    """ Connect to VeChain """

    def __init__(self, url):
        self.url = url

    def get_account(self, address: str, block: str = "best") -> dict:
        """ Query account status against the "best" block (or your choice)"""
        url = build_url(self.url, f"/accounts/{address}?revision={block}")
        r = requests.get(url, headers={"accept": "application/json"})
        if not (r.status_code == 200):
            raise Exception(f"Cant connect to {url}, error {r.text}")
        return r.json()

    def get_block(self, id_or_number: str = "best") -> dict:
        """ Get a block by id or number, default get "best" block """
        url = build_url(self.url, f"blocks/{id_or_number}")
        r = requests.get(url, headers={"accept": "application/json"})
        if not (r.status_code == 200):
            raise Exception(f"Cant connect to {url}, error {r.text}")
        return r.json()

    def get_chainTag(self) -> int:
        """ Fetch ChainTag from the remote network """
        b = self.get_block(0)
        return calc_chaintag(b["id"][-2:])

    def get_tx(self, tx_id: str) -> Union[dict, None]:
        """ Fetch a transaction, if not found then None """
        url = build_url(self.url, f"/transactions/{tx_id}")
        r = requests.get(url, headers={"accept": "application/json"})
        if not (r.status_code == 200):
            raise Exception(f"Cant connect to {url}, error {r.text}")
        return r.json()

    def emulate(self, emulate_tx_body: dict, block: str = "best") -> List[dict]:
        """
        Helper function. Use with caution.
        Upload a tx body for emulation,
        Get a list of execution responses (as the tx has multiple clauses).
        The response json structure please view README.md

        Parameters
        ----------
        emulate_tx_body : dict
            Emulate Tx body, not a normal tx body.
        block : str, optional
            Target at which block, by default "best"

        Returns
        -------
        List[dict]
            A list of clause execution results. (within the tx)

        Raises
        ------
        Exception
            If http has error.
        """
        url = build_url(self.url, f"/accounts/*?revision={block}")
        r = requests.post(
            url,
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json=emulate_tx_body,
        )
        if not (r.status_code == 200):
            raise Exception(f"HTTP error: {r.status_code} {r.text}")

        all_responses = r.json()
        for response in all_responses:
            if response["reverted"] == True and response["data"] != "0x":
                response["decoded"] = {
                    "revertReason": calc_revertReason(response["data"])
                }
        return all_responses

    def replay_tx(self, tx_id: str) -> List[dict]:
        """
        Use the emulate function to replay the tx softly (for debug)
        Usually when you replay the tx to see what's wrong.

        Parameters
        ----------
        tx_id : str
            Existing tx id

        Returns
        -------
        List[dict]
            A list of clause execution results. (within the tx)

        Raises
        ------
        Exception
            If tx id doesn't exist
        """
        tx = self.get_tx(tx_id)
        if not tx:
            raise Exception(f"tx: {tx_id} not found")

        caller = tx["origin"]
        target_block = tx["meta"]["blockID"]
        emulate_body = calc_emulate_tx_body(caller, tx)
        if tx["delegator"]:
            emulate_body["gasPayer"] = tx["delegator"]

        return self.emulate(emulate_body, target_block)

    def emulate_tx(self, address: str, tx_body: dict, block: str = "best"):
        """
        Use the emulate function to emulate execution of a transaction.
        """
        emulate_body = calc_emulate_tx_body(address, tx_body)
        return self.emulate(emulate_body, block)

    def call(
        self,
        caller: str,
        contract: Contract,
        func_name: str,
        params: List,
        to: str,
        value=0,
        gas=0,
    ):
        """
        Call a contract method (read-only), this won't create change on blockchain.
        Only emulation happens. Response type view README.md.
        This is a single transaction, single clause call.

        If function has return value, it will be included in "decoded".
        """
        abi_dict = contract.get_abi(func_name)
        if not abi_dict:
            raise Exception(f"Function {func_name} not found on the contract")

        # if not is_readonly(abi_dict):
        #     raise Exception(
        #         f"Function {func_name} is not read-only, it is {abi_dict['stateMutability']}"
        #     )

        f = abi.Function(abi.FUNCTION(abi_dict))
        data = f.encode(params, to_hex=True)  # Tx clause data
        clause = {"to": to, "value": str(value), "data": data}
        tx_body = build_tx_body(
            [clause],
            self.get_chainTag(),
            calc_blockRef(self.get_block("best")["id"]),
            calc_nonce(),
            gas=gas,
        )

        e_response = self.emulate_tx(caller, tx_body)
        failed = any_emulate_failed(e_response)
        if failed:
            return e_response
        else:
            first_clause = e_response[0]
            # decode the "return data" from the function call
            if first_clause["data"] and first_clause["data"] != "0x":
                first_clause["decoded"] = f.decode(
                    bytes.fromhex(first_clause["data"][2:])  # Remove '0x'
                )
            # decode the "event" from the function call
            if len(first_clause["events"]):
                for each_event in first_clause["events"]:
                    if each_event["address"].lower() == to.lower():
                        e_obj = contract.get_event_by_signature(
                            bytes.fromhex(each_event["topics"][0][2:])
                        )
                        if e_obj:
                            each_event["decoded"] = e_obj.decode(
                                bytes.fromhex(each_event["data"][2:]),
                                [bytes.fromhex(x[2:]) for x in each_event["topics"]],
                            )
                            each_event["name"] = e_obj.get_name()
            return first_clause

    def commit(
        self,
        wallet: Wallet,
        contract: Contract,
        func_name: str,
        params: List,
        to,
        value=0,
        gas=0,
    ):
        """ Call a contract method (not emulate), will create change to blockchain """
        pass

    def deploy(self, wallet: Wallet, contract: Contract):
        """ Deploy a smart contract onto blockchain """
        pass

    # def build_tx(
    #     self, wallet: Wallet, to, value, data, gas: int = None, dependsOn=None
    # ) -> dict:
    #     """ Build Tx, sign it and estimate gas for it """
    #     block = self.get_block("best")
    #     blockRef = calc_blockRef(block["id"])
    #     nonce = calc_nonce()
    #     chainTag = self.get_chainTag()
    #     body = {
    #         "chainTag": chainTag,  #
    #         "blockRef": blockRef,
    #         "expiration": 32,
    #         "clauses": [{"to": to, "value": value, "data": data}],
    #         "gasPriceCoef": 0,  #
    #         # "gas": gas,
    #         "dependsOn": dependsOn,  #
    #         "nonce": nonce,  #
    #     }

    #     responses = self.emulate_tx_body(wallet, body)
    #     if any_emulate_failed(responses):
    #         raise Exception(f"Emulation failed: {responses}")

    #     gases = read_vm_gases(responses)
    #     if gas and gas < gases[0]:
    #         raise Exception(f"gas {gas} < emulated vm gas result {gases[0]}")

    #     body["gas"] = 0
    #     tx = transaction.Transaction(body)
    #     intrinsic_gas = tx.get_intrinsic_gas()

    #     if gas:
    #         body["gas"] = gas + intrinsic_gas + 15000
    #     else:
    #         body["gas"] = gases[0] + intrinsic_gas + 15000

    #     return body