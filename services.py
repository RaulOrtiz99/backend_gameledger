# backend/services.py
from web3 import Web3
import json
from config import w3


def prepare_transaction(contract_addr: str, abi_path: str, function: str, args: list):
    with open(abi_path, 'r') as f:
        abi = json.load(f)

    contract = w3.eth.contract(address=contract_addr, abi=abi)
    fn = contract.get_function_by_name(function)

    tx = fn(*args).build_transaction({
        "chainId": 4202,
        "gas": 300000,
        "gasPrice": w3.eth.gas_price,
        # ← Usa la wallet del backend
        "nonce": w3.eth.get_transaction_count("0x..."),
    })

    return tx
