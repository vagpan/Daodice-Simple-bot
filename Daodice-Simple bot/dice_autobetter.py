import time
from my_converter import *
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from configu import BASE_DOMAIN_URL_V3_FOR_TEST
from iconsdk.builder.transaction_builder import (CallTransactionBuilder)

icon_service = IconService(HTTPProvider(BASE_DOMAIN_URL_V3_FOR_TEST))
nid = 1
daoDice_contract = "cxb0b6f777fba13d62961ad8ce11be7ef6c4b2bcc6"

loops = 5
lower = 0
upper = 94
bet = 0.15

# Put your wallet's keystore name and password
wallet = KeyWallet.load("./", "")
print()
print("Your Wallet address: ", wallet.get_address(), " ---Your private key: ", wallet.get_private_key())
icx_balance = from_bigint(icon_service.get_balance(wallet.get_address()))
print(f"Your icx balance is {icx_balance:5.2f} Icx. \tYou are playing at {(upper - lower) + 1}% chance")

# Conditions for a valid bet
if not (0 <= upper <= 99 and 0 <= lower <= 99):
    print("Numbers out of range. Invalid Bet")
    exit()
if not (0 <= upper - lower <= 95):
    print("Bet placed with illegal gap")
    exit()
if isinstance(bet, int):
    bet = int_to_bigint(bet)

else:
    bet = float_value(bet)

# Params for the contract call. You can write a lucky phrase in user_seed if you want to.
params = {
    "upper": hex(upper),
    "lower": hex(lower),
    "user_seed": ""
}


def dice_fast_bets(bet_amount, params_bet, loop_times):
    signed_tx = []
    for _ in range(loop_times):
        transaction = CallTransactionBuilder() \
            .from_(wallet.get_address()) \
            .to(daoDice_contract) \
            .step_limit(40000000) \
            .value(bet_amount) \
            .nid(nid) \
            .nonce(50) \
            .method("call_bet") \
            .params(params_bet) \
            .build()
        # Signs and sends the tx to the contract
        signed_transaction = SignedTransaction(transaction, wallet)
        signed_tx.append(signed_transaction)

    return signed_tx


# Create a list of all the signed txs  before we send them.
list_of_signed_txs = dice_fast_bets(bet, params, loops)

# We send all the signed tx.
if icx_balance > 2:
    for every_tx in list_of_signed_txs:
        tx_hash = icon_service.send_transaction(every_tx)

    else:
        print()
        print("Done. Check the tracker for more info")
        print(f"\nBalance: {icx_balance:5.2f} Icx")
else:
    print("No icx left to bet. Bot exits")
    exit()
