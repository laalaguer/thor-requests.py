import time
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
    calc_tx_signed,
    calc_tx_unsigned,
    read_vm_gases,
    calc_gas,
    build_params,
)
from .wallet import Wallet
from .contract import Contract


class Connect:
    """Connect to VeChain"""

    def __init__(self, url):
        self.url = url

    def get_account(self, address: str, block: str = "best") -> dict:
        """Query account status against the "best" block (or your choice)"""
        url = build_url(self.url, f"/accounts/{address}?revision={block}")
        r = requests.get(url, headers={"accept": "application/json"})
        if not (r.status_code == 200):
            raise Exception(f"Cant connect to {url}, error {r.text}")
        return r.json()

    def get_block(self, id_or_number: str = "best") -> dict:
        """Get a block by id or number, default get "best" block"""
        url = build_url(self.url, f"blocks/{id_or_number}")
        r = requests.get(url, headers={"accept": "application/json"})
        if not (r.status_code == 200):
            raise Exception(f"Cant connect to {url}, error {r.text}")
        return r.json()

    def get_chainTag(self) -> int:
        """Fetch ChainTag from the remote network"""
        b = self.get_block(0)
        return calc_chaintag(b["id"][-2:])

    def get_tx(self, tx_id: str) -> Union[dict, None]:
        """Fetch a transaction, if not found then None"""
        url = build_url(self.url, f"/transactions/{tx_id}")
        r = requests.get(url, headers={"accept": "application/json"})
        if not (r.status_code == 200):
            raise Exception(f"Cant connect to {url}, error {r.text}")
        return r.json()

    def post_tx(self, raw: str) -> dict:
        """
        Post tx to remote node. Get response.

        Parameters
        ----------
        raw : str
            '0x....' raw tx

        Returns
        -------
        dict
            post response eg. {'id': '0x....'}

        Raises
        ------
        Exception
            http exception
        """
        url = build_url(self.url, "transactions")
        r = requests.post(
            url,
            headers={"accept": "application/json", "Content-Type": "application/json"},
            json={"raw": raw},
        )
        if not (r.status_code == 200):
            raise Exception(f"Creation error? HTTP: {r.status_code} {r.text}")

        return r.json()

    def get_tx_receipt(self, tx_id: str) -> Union[dict, None]:
        """Fetch tx receipt as a dict, or None"""
        url = build_url(self.url, f"transactions/{tx_id}/receipt")
        r = requests.get(url, headers={"accept": "application/json"})
        if not (r.status_code == 200):
            raise Exception(f"Creation error? HTTP: {r.status_code} {r.text}")

        return r.json()

    def wait_for_tx_receipt(self, tx_id: str, timeout: int = 20) -> Union[dict, None]:
        """
        Wait for tx receipt, for several seconds

        Parameters
        ----------
        tx_id : str
            tx id
        timeout : int, optional
            seconds, by default 20

        Returns
        -------
        dict
            The receipt or None
        """
        interval = 3
        rounds = timeout // interval
        receipt = None
        for _ in range(rounds):
            receipt = self.get_tx_receipt(tx_id)
            if receipt:
                return receipt
            else:
                time.sleep(3)
        return None

    def emulate(self, emulate_tx_body: dict, block: str = "best") -> List[dict]:
        """
        Helper function.
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
        # Decode the "revert" reason if emulation failed
        # Create a "revertReason" in the body with plain text reason
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
            See emulate()

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
        Emulate the execution of a transaction.

        Parameters
        ----------
        address : str
            '0x...' address of caller.
        tx_body : dict
            Tx body to be emulated
        block : str, optional
            Target at which block? by default "best"

        Returns
        -------
        List[dict]
            See emulate()
        """
        emulate_body = calc_emulate_tx_body(address, tx_body)
        return self.emulate(emulate_body, block)

    def clause(
        self,
        contract: Contract,
        func_name: str,
        func_params: List,
        to: str,
        value=0,
    ) -> dict:
        """
        Build a clause according to the function name and params.
        raise Exception when function is not found by name.

        Parameters
        ----------
        contract : Contract
            On which contract the function is sitting.
        func_name : str
            Name of the function.
        func_params : List
            Function params supplied by users.
        to : str
            Address of the contract.
        value : int, optional
            VET sent with the clause in Wei, by default 0

        Returns
        -------
        dict
            The clause as a dict: {"to":, "value":, "data":}
        """
        f = contract.get_function_by_name(func_name, strict_mode=True)
        data = f.encode(func_params, to_hex=True)  # Tx clause data
        a_clause = {"to": to, "value": str(value), "data": data}
        return a_clause

    def call(
        self,
        caller: str,
        contract: Contract,
        func_name: str,
        func_params: List,
        to: str,
        value=0,
        gas=0,  # Note: value is in Wei
    ) -> dict:
        """
        Call a contract method (read-only).
        This is a single transaction, single clause call.
        This WON'T create ANY change on blockchain.
        Only emulation happens.

        Response type view README.md
        If function has any return value, it will be included in "decoded" field
        """
        # Get the clause object
        clause = self.clause(contract, func_name, func_params, to, value)
        # Build tx body
        tx_body = build_tx_body(
            [clause],
            self.get_chainTag(),
            calc_blockRef(self.get_block("best")["id"]),
            calc_nonce(),
            gas=gas,
        )

        # Emulate the Tx first
        e_responses = self.emulate_tx(caller, tx_body)
        assert len(e_responses) == 1
        failed = any_emulate_failed(e_responses)
        if failed:
            return e_responses[0]
        else:
            first_clause = e_responses[0]
            # decode the "return data" from the function call
            if first_clause["data"] and first_clause["data"] != "0x":
                f_obj = contract.get_function_by_name(func_name, strict_mode=True)
                first_clause["decoded"] = f_obj.decode(
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

    def call_multi(self, caller: str, clauses: List, gas: int = 0) -> dict:
        """
        Call a contract method (read-only).
        This is a single transaction, multi-clause call.
        This WON'T create ANY change on blockchain.
        Only emulation happens.

        Response type view README.md
        If the called functions has any return value, it will be included in "decoded" field
        """
        # Build tx body
        tx_body = build_tx_body(
            [clauses],
            self.get_chainTag(),
            calc_blockRef(self.get_block("best")["id"]),
            calc_nonce(),
            gas=gas,
        )

    def transact(
        self,
        wallet: Wallet,
        contract: Contract,
        func_name: str,
        func_params: List,
        to: str,
        value=0,  # Note: value is in Wei
        gas=0,
    ) -> dict:
        """
        Call a contract method,
        Similar to "call()" but will create state change to blockchain.
        And will spend real gas.
        This would be a single clause transaction.

        Parameters
        ----------
        wallet : Wallet
            Function Caller wallet
        contract : Contract
            Smart contract meta
        func_name : str
            Function name
        func_params: list
            Function params. eg. ['0x123..efg', '100']
        value:
            VET in Wei to send with this call
        gas:
            Gas you willing to pay to power this contract call.

        Returns
        -------
            Return value see post_tx()
        """
        clause = self.clause(contract, func_name, func_params, to, value)
        tx_body = build_tx_body(
            [clause],
            self.get_chainTag(),
            calc_blockRef(self.get_block("best")["id"]),
            calc_nonce(),
            gas=gas,
        )

        # Emulate the tx first.
        e_responses = self.emulate_tx(wallet.getAddress(), tx_body)
        if any_emulate_failed(e_responses):
            raise Exception(f"Tx will revert: {e_responses}")

        # Get gas estimation from remote node
        # Calculate a safe gas for user
        _vm_gases = read_vm_gases(e_responses)
        _supposed_vm_gas = _vm_gases[0]
        _tx_obj = calc_tx_unsigned(tx_body)
        _intrincis_gas = _tx_obj.get_intrinsic_gas()
        _supposed_safe_gas = calc_gas(_supposed_vm_gas, _intrincis_gas)
        if gas and gas < _supposed_safe_gas:
            raise Exception(f"gas {gas} < emulated gas {_supposed_safe_gas}")

        # Fill out the gas for user
        if not gas:
            tx_body["gas"] = _supposed_safe_gas

        # Post it to the remote node
        encoded_raw = calc_tx_signed(wallet, tx_body, True)
        return self.post_tx(encoded_raw)

    def transact_multi():
        pass

    def deploy(
        self,
        wallet: Wallet,
        contract: Contract,
        params_types: list = None,  # Constructor params types
        params: list = None,  # Constructor params
        value=0,  # send VET in Wei with constructor call
    ) -> dict:
        """
        Deploy a smart contract to blockchain
        This is a single clause transaction.

        Parameters
        ----------
        wallet : Wallet
            Deployer wallet
        contract : Contract
            Smart contract meta
        params_types : list
            Constructor call parameter types. eg. ['address', 'uint256']
        params: list
            constructor call params. eg. ['0x123..efg', '100']
        value:
            VET in Wei to send with deploy call

        Returns
        -------
            Return value see post_tx()
        """
        # Build the constructor call data.
        if not params_types:
            data_bytes = contract.get_bytecode()
        else:
            data_bytes = contract.get_bytecode() + build_params(params_types, params)
        data = "0x" + data_bytes.hex()

        # Build the tx body.
        clause = {"to": None, "value": str(value), "data": data}
        tx_body = build_tx_body(
            [clause],
            self.get_chainTag(),
            calc_blockRef(self.get_block("best")["id"]),
            calc_nonce(),
            gas=0,  # We will estimate the gas later
        )

        # We emulate it first.
        e_responses = self.emulate_tx(wallet.getAddress(), tx_body)
        if any_emulate_failed(e_responses):
            raise Exception(f"Tx will revert: {e_responses}")

        # Get gas estimation from remote
        _vm_gases = read_vm_gases(e_responses)
        _supposed_vm_gas = _vm_gases[0]
        _tx_obj = calc_tx_unsigned(tx_body)
        _intrincis_gas = _tx_obj.get_intrinsic_gas()
        _supposed_safe_gas = calc_gas(_supposed_vm_gas, _intrincis_gas)

        # Fill out the gas for user.
        tx_body["gas"] = _supposed_safe_gas

        encoded_raw = calc_tx_signed(wallet, tx_body, True)
        return self.post_tx(encoded_raw)
