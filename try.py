from thor_requests.connect import Connect
from thor_requests.wallet import Wallet
from thor_requests.contract import Contract

w = Wallet.fromPrivateKey(
    bytes.fromhex("dce1443bd2ef0c2631adc1c67e5c93f13dc23a41c18b536effbbdcbcdb96fb65")
)
c = Connect("http://testnet.veblocks.net")
# print(c.get_tx("0xda2ce6bddfb3bd32541c999e81ef56019a6314a23c90a466896aeefca33aebc1"))
print(c.replay_tx("0x1d05a502db56ba46ccd258a5696b9b78cd83de6d0d67f22b297f37e710a72bb5"))

# print(c.replay_tx("0x913011bcc1b351436e5296c821fff066c5296f9f95646345eda92fdeade4e8f6"))
# vvet_contract = Contract.fromFile("./VVET9.json")
# vvet_addr = "0x535b9a56c2f03a3658fc8787c44087574eb381fd"

# # <Emulate call> the "balanceOf()" function
# res = c.call(
#     w.getAddress(),
#     vvet_contract,
#     "balanceOf",
#     [w.getAddress()],
#     vvet_addr,
# )
# print(res)

# # <Emulate call> the "depost()" function.
# res = c.call(w.getAddress(), vvet_contract, "deposit", [], vvet_addr, value=4)
# print(res)

# # <Real call> the "deposit()" function. (will pay gas)
# res = c.commit(w, vvet_contract, "deposit", [], vvet_addr, value=5 * (10 ** 18))
# print(res)

# # <Deploy> the smart contract
# res = c.deploy(w, vvet_contract, None, None, 0)
# print(res)

# # Get name from smart contracts
# uniswap_v2_pair = Contract.fromFile("./UniswapV2Pair.json")
# print(uniswap_v2_pair.get_contract_name())