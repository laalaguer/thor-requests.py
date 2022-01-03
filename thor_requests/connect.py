import time
import json
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
    calc_tx_signed,
    calc_tx_signed_with_fee_delegation,
    inject_decoded_event,
    inject_decoded_return,
    inject_revert_reason,
    is_emulate_failed,
    read_vm_gases,
    build_params,
    suggest_gas_for_tx,
)
from .wallet import Wallet
from .contract import Contract
from .clause import Clause
from .const import VTHO_ABI, VTHO_ADDRESS


def _beautify(response: dict, contract: Contract, func_name: str) -> dict:
    ''' Beautify a emulation response dict, to include decoded return and decoded events '''
    # Decode return value
    response = inject_decoded_return(response, contract, func_name)
    # Decode events (if any)
    if not len(response["events"]):  # no events just return
        return response

    response["events"] = [
        inject_decoded_event(each_event, contract)
        for each_event in response["events"]
    ]

    return response


class Connect:
    """Connect to VeChain"""

    def __init__(self, url, timeout: float = 20):
        '''
        Create a new connector to VeChain

        Parameters
        ----------
        url : str
            VeChain node url
        timeout : float, optional
            timeout (in seconds) on POST/GET when connecting to VeChain, by default 20
        '''
        self.url = url
        self.timeout = timeout

    def get_endpoint(self):
        '''Return which node current connector is linked to'''
        return self.url

    def set_timeout(self, timeout: float):
        """Adjust the time out for the connector in seconds"""
        self.timeout = float(timeout)

    def get_account(self, address: str, block: str = "best") -> dict:
        """Query account status against the "best" block (or your choice)"""
        url = build_url(self.url, f"/accounts/{address}?revision={block}")
        r = requests.get(
            url, headers={"accept": "application/json"}, timeout=self.timeout
        )
        if not (r.status_code == 200):
            raise Exception(f"Cant connect to {url}, error {r.text}")
        return r.json()

    def get_vet_balance(self, address: str, block: str = "best") -> int:
        """
        Query the vet balance of an account

        Parameters
        ----------
        address : str
            The address of the account
        block : str, optional
            Query against which block, the block ID or number, by default "best"

        Returns
        -------
        int
            The balance of the VET in Wei
        """
        account_status = self.get_account(address)
        return int(account_status["balance"], 16)

    def get_vtho_balance(self, address: str, block: str = "best") -> int:
        """
        Query the vtho balance of an account

        Parameters
        ----------
        address : str
            The address of the account
        block : str, optional
            Query against which block, the block ID or number, by default "best"

        Returns
        -------
        int
            The balance of the VTHO in Wei
        """
        account_status = self.get_account(address)
        return int(account_status["energy"], 16)

    def get_block(self, id_or_number: str = "best") -> dict:
        """Get a block by id or number, default get "best" block"""
        url = build_url(self.url, f"blocks/{id_or_number}")
        r = requests.get(
            url, headers={"accept": "application/json"}, timeout=self.timeout
        )
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
        r = requests.get(
            url, headers={"accept": "application/json"}, timeout=self.timeout
        )
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
            headers={"accept": "application/json",
                     "Content-Type": "application/json"},
            json={"raw": raw},
            timeout=self.timeout
        )
        if not (r.status_code == 200):
            raise Exception(f"Creation error? HTTP: {r.status_code} {r.text}")

        return r.json()

    def get_tx_receipt(self, tx_id: str) -> Union[dict, None]:
        """Fetch tx receipt as a dict, or None"""
        url = build_url(self.url, f"transactions/{tx_id}/receipt")
        r = requests.get(
            url, headers={"accept": "application/json"}, timeout=self.timeout
        )
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

    def ticker(self) -> dict:
        '''
        Yields the block one by one

        Yields
        -------
        Iterator[dict]
            The block, one by one
        '''
        sleep_second = 1
        cache = self.get_block('best')
        while True:
            new_block = self.get_block('best')
            if new_block['id'] != cache['id']:
                cache = new_block
                yield new_block
            else:
                time.sleep(sleep_second)

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
            headers={"accept": "application/json",
                     "Content-Type": "application/json"},
            json=emulate_tx_body,
            timeout=self.timeout,
        )
        if not (r.status_code == 200):
            raise Exception(f"HTTP error: {r.status_code} {r.text}")

        all_responses = r.json()  # A list of responses
        return list(map(inject_revert_reason, all_responses))

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

    def emulate_tx(self, address: str, tx_body: dict, block: str = "best", gas_payer: str = None):
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
        emulate_body = calc_emulate_tx_body(address, tx_body, gas_payer)
        return self.emulate(emulate_body, block)

    def clause(
        self,
        contract: Contract,
        func_name: str,
        func_params: List,
        to: str,
        value=0,
    ) -> Clause:
        """
        There are two types of calls:
        1) Function call on a smart contract
        Build a clause according to the function name and params.
        raise Exception when function is not found by name.

        2) Pure transfer of VET
        Set the contract, func_name, and func_params to None

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
        return Clause(to, contract, func_name, func_params, value)

    def call(
        self,
        caller: str,
        contract: Contract,
        func_name: str,
        func_params: List,
        to: str,
        value=0,
        gas=0,  # Note: value is in Wei
        gas_payer: str = None,  # Note: gas payer of the tx
        block: str = "best"  # Target at which block
    ) -> dict:
        """
        Call a contract method (read-only).
        This is a single transaction, single clause call.
        This WON'T create ANY change on blockchain.
        Only emulation happens.

        Response type view README.md
        If function has any return value, it will be included in "decoded" field
        """
        # Get the Clause object
        clause = self.clause(contract, func_name, func_params, to, value)
        # Build tx body
        need_fee_delegation = gas_payer != None
        tx_body = build_tx_body(
            [clause.to_dict()],
            self.get_chainTag(),
            calc_blockRef(self.get_block("best")["id"]),
            calc_nonce(),
            gas=gas,
            feeDelegation=need_fee_delegation
        )

        # Emulate the Tx
        e_responses = self.emulate_tx(
            caller, tx_body, block=block, gas_payer=gas_payer)
        # Should only have one response, since we only have 1 clause
        assert len(e_responses) == 1

        # If emulation failed just return the failed response.
        if any_emulate_failed(e_responses):
            return e_responses[0]

        return _beautify(e_responses[0], clause.get_contract(), clause.get_func_name())

    def call_multi(self, caller: str, clauses: List[Clause], gas: int = 0, gas_payer: str = None, block="best") -> List[dict]:
        """
        Call a contract method (read-only).
        This is a single transaction, multi-clause call.
        This WON'T create ANY change on blockchain.
        Only emulation happens.

        Response type view README.md
        If the called functions has any return value, it will be included in "decoded" field
        """
        need_fee_delegation = gas_payer != None
        # Build tx body
        tx_body = build_tx_body(
            [clause.to_dict() for clause in clauses],
            self.get_chainTag(),
            calc_blockRef(self.get_block("best")["id"]),
            calc_nonce(),
            gas=gas,
            feeDelegation=need_fee_delegation
        )

        # Emulate the Tx
        e_responses = self.emulate_tx(
            caller, tx_body, block=block, gas_payer=gas_payer)
        assert len(e_responses) == len(clauses)

        # Try to beautify the responses
        _responses = []
        for response, clause in zip(e_responses, clauses):
            # Failed response just ouput plain response
            if is_emulate_failed(response):
                _responses.append(response)
                continue
            # Success response inject beautified decoded data
            _responses.append(
                _beautify(response, clause.get_contract(), clause.get_func_name()))

        return _responses

    def transact(
        self,
        wallet: Wallet,
        contract: Contract,
        func_name: str,
        func_params: List,
        to: str,
        value: int = 0,  # Note: value is in Wei
        gas: int = 0,
        force: bool = False,  # Force execute even if emulation failed
        gas_payer: Wallet = None  # fee delegation feature
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
        force:
            Force execution even if emulation failed.
        gas_payer:
            The user wallet to pay for the transaction.

        Returns
        -------
            Return value see post_tx()
        """
        clause = self.clause(contract, func_name, func_params, to, value)
        need_fee_delegation = gas_payer != None
        tx_body = build_tx_body(
            [clause.to_dict()],
            self.get_chainTag(),
            calc_blockRef(self.get_block("best")["id"]),
            calc_nonce(),
            gas=gas,
            feeDelegation=need_fee_delegation
        )

        # Emulate the tx first.
        if not need_fee_delegation:
            e_responses = self.emulate_tx(wallet.getAddress(), tx_body)
        else:
            e_responses = self.emulate_tx(
                wallet.getAddress(), tx_body, gas_payer=gas_payer.getAddress())

        if any_emulate_failed(e_responses) and force == False:
            raise Exception(f"Tx will revert: {e_responses}")

        # Get gas estimation from remote node
        # Calculate a safe gas for user
        vm_gas = sum(read_vm_gases(e_responses))
        safe_gas = suggest_gas_for_tx(vm_gas, tx_body)
        if gas and gas < safe_gas:
            if force == False:
                raise Exception(f"gas {gas} < emulated gas {safe_gas}")

        # Fill out the gas for user
        if not gas:
            tx_body["gas"] = safe_gas

        # Post it to the remote node
        if not need_fee_delegation:
            encoded_raw = calc_tx_signed(wallet, tx_body, True)
        else:
            encoded_raw = calc_tx_signed_with_fee_delegation(
                wallet, gas_payer, tx_body, True)
        return self.post_tx(encoded_raw)

    def transact_multi(
        self, wallet: Wallet, clauses: List[Clause], gas: int = 0, force: bool = False, gas_payer: Wallet = None
    ):
        # Emulate the whole tx first.
        if gas_payer:
            e_responses = self.call_multi(
                wallet.getAddress(), clauses, gas, gas_payer=gas_payer.getAddress())
        else:
            e_responses = self.call_multi(wallet.getAddress(), clauses, gas)
        if any_emulate_failed(e_responses) and force == False:
            raise Exception(f"Tx will revert: {e_responses}")

        need_fee_delegation = gas_payer != None
        # Build the body
        tx_body = build_tx_body(
            [clause.to_dict() for clause in clauses],
            self.get_chainTag(),
            calc_blockRef(self.get_block("best")["id"]),
            calc_nonce(),
            gas=gas,
            feeDelegation=need_fee_delegation
        )

        # Get gas estimation from remote node
        # Calculate a safe gas for user
        vm_gas = sum(read_vm_gases(e_responses))
        safe_gas = suggest_gas_for_tx(vm_gas, tx_body)
        if gas and gas < safe_gas:
            if force == False:
                raise Exception(f"gas {gas} < emulated gas {safe_gas}")

        # Fill out the gas for user
        if not gas:
            tx_body["gas"] = safe_gas

        # Post it to the remote node
        if not need_fee_delegation:
            encoded_raw = calc_tx_signed(wallet, tx_body, True)
        else:
            encoded_raw = calc_tx_signed_with_fee_delegation(
                wallet, gas_payer, tx_body, True)
        return self.post_tx(encoded_raw)

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
        vm_gas = sum(read_vm_gases(e_responses))
        safe_gas = suggest_gas_for_tx(vm_gas, tx_body)

        # Fill out the gas for user.
        tx_body["gas"] = safe_gas

        encoded_raw = calc_tx_signed(wallet, tx_body, True)
        return self.post_tx(encoded_raw)

    def transfer_vet(self, wallet: Wallet, to: str, value: int = 0, gas_payer: Wallet = None) -> dict:
        """
        Convenient function: do a pure VET transfer

        Parameters
        ----------
        to : str
            Address of the receiver
        value : int, optional
            Amount of VET to transfer in Wei, by default 0

        Returns
        -------
        dict
            See post_tx()
        """
        return self.transact(wallet, None, None, None, to, value, gas_payer=gas_payer)

    def transfer_vtho(self, wallet: Wallet, to: str, vtho_in_wei: int = 0, gas_payer: Wallet = None) -> dict:
        '''
        Convenient function: do a pure vtho transfer

        Parameters
        ----------
        wallet : Wallet
            The sender's wallet
        to : str
            The receiver's address
        vtho_in_wei : int, optional
            Amount of VTHO (in Wei) to send to receiver, by default 0

        Returns
        -------
        dict
            See post_tx()
        '''
        _contract = Contract({"abi": json.loads(VTHO_ABI)})
        return self.transact(wallet, _contract, 'transfer', [to, vtho_in_wei], VTHO_ADDRESS, gas_payer=gas_payer)
