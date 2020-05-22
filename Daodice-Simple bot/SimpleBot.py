import time
from my_converter import *
from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet
from configu import BASE_DOMAIN_URL_V3_FOR_TEST
from iconsdk.builder.transaction_builder import (CallTransactionBuilder)

icon_service = IconService(HTTPProvider(BASE_DOMAIN_URL_V3_FOR_TEST))

nid=3 # 3 for testnet, 1 for mainnet
daoDice_contract="cxe2b43dba05f889fb3a99b480817675fac1fb3ec3"



# You can change loops, lower-upper range for the odds, the base bet and the wait-time for speed (let it  min at 4 sec)
loops = 100
lower = 0
upper = 94
bet = 0.4 # IMPORTANT. Its the initial bet only. You have to change the bets below for the loss streak.
wait_time = 5


# Loads the gambling wallet
wallet = KeyWallet.load("./", "")
print()
print("Your Wallet address: ", wallet.get_address(), " ---Your private key: ", wallet.get_private_key())
icx_balance = from_bigint(icon_service.get_balance(wallet.get_address()))
print(f"Your icx balance is {icx_balance:5.2f} Icx. \tYou are playing at {(upper-lower)+1}% chance")

# IMPORTANT Don't change the loss counter.
bet_counter = 1
loss_streak_counter = 0
_min_bet= 0.1


# Checks your bet to be valid.
if not (0 <= upper <= 99 and 0 <= lower <= 99):
    print("Numbers out of range. Invalid Bet")
    exit()
if not (0 <= upper - lower <= 95):
    print("Bet placed with illegal gap")
    exit()

print("\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t--- Bot is starting for Daodice. Good Luck! ---\n")
print("\tResult\t\t\t\tBalance\t\t\t\tCurrent Bet\t\t\t\tWinning Number\t\t\t\t Range\t\t\t\t #Bet\t\t\t\t\t\t\t\tHash")
print("---------------------------------------------------------------------------------------------------------------"\
      "---------------------------------------------------------------------------------------------------------------")


def dice_bot(next_bet, loss_streak, bet_count):
    # Checks for integer or float bet amount and converts it
    if isinstance(next_bet, int):
        next_bet = int_to_bigint(next_bet)

    else:
        next_bet = float_value(next_bet)
    # Params for the contract call. You can write a lucky phrase in user_seed if you want to.
    params = {
        "upper": hex(upper),
        "lower": hex(lower),
        "user_seed": ""
    }

    transaction = CallTransactionBuilder() \
        .from_(wallet.get_address()) \
        .to(daoDice_contract) \
        .step_limit(40000000) \
        .value(next_bet) \
        .nid(nid) \
        .nonce(50) \
        .method("call_bet") \
        .params(params) \
        .build()
    # Signs and sends the tx to the contract
    signed_transaction = SignedTransaction(transaction, wallet)
    tx_hash = icon_service.send_transaction(signed_transaction)

    # Important to put some delay to get the result of your bet. 4sec is enough but its better to put some bigger number
    time.sleep(wait_time)

    tx_result = icon_service.get_transaction_result(tx_hash)

    # Finding the range
    if tx_result["eventLogs"][3]["indexed"][0] == "BetPlaced(int,int,int)":
        my_bet_range = tx_result["eventLogs"][3]["indexed"]
        my_bet_range = sorted([from_hex(dice) for dice in my_bet_range[2:]])

    else:
        for i in tx_result["eventLogs"]:
            if i["indexed"][0] == "BetPlaced(int,int,int)":
                my_bet_range = sorted([from_hex(dice) for dice in i["indexed"][2:]])
                break


    if tx_result["eventLogs"][4]["indexed"][0] == "BetResult(str,int,int)":
        bet_result = tx_result["eventLogs"][4]["indexed"]
        winning_number = from_hex(bet_result[2])
    else:
        for i in tx_result["eventLogs"]:
            if i["indexed"][0] == 'BetResult(str,int,int)':
                winning_number = from_hex(i["indexed"][2])
                break

    # You can change the bet amounts after a loss streak or return to your base bet.
    bet_value = [0.2, 0.8, 1.6, 3.2]
    # A counter checks for number of lose streaks, changing the bet and reseting after a win.
    if lower <= winning_number <= upper:
        bet_count += 1
        loss_streak = 0
        print(
            f"\tWIN   \t\t\t\t{icx_balance:6.2f}\t\t\t\t{from_bigint(next_bet):5.2f}\t\t\t\t\t\t{winning_number:2}\
             \t\t\t{my_bet_range[0]:2}-{my_bet_range[1]:2}\t\t\t\t{bet_counter:4}\t\t\t{tx_hash}")
        next_bet = bet_value[0]

    else:
        loss_streak += 1
        bet_count += 1
        if loss_streak == 1:
            print(
                f"-->  LOSS(x1)\t\t\t{icx_balance:6.2f}\t\t\t\t{from_bigint(next_bet):5.2f}\t\t\t\t\t\t{winning_number:2}\
             \t\t\t{my_bet_range[0]:2}-{my_bet_range[1]:2}\t\t\t\t{bet_counter:4}\t\t\t{tx_hash}")
            next_bet = bet_value[1]
        elif loss_streak == 2:
            print(
                f"-->  LOSS(X2)\t\t\t\t{icx_balance:6.2f}\t\t\t\t{from_bigint(next_bet):5.2f}\t\t\t\t\t\t{winning_number:2}\
             \t\t\t{my_bet_range[0]:2}-{my_bet_range[1]:2}\t\t\t\t{bet_counter:4}\t\t\t{tx_hash}")
            next_bet = bet_value[2]
        elif loss_streak == 3:
            print(
                f"-->  LOSS(X3)\t\t\t\t{icx_balance:6.2f}\t\t\t\t{from_bigint(next_bet):5.2f}\t\t\t\t\t\t{winning_number:2}\
             \t\t\t{my_bet_range[0]:2}-{my_bet_range[1]:2}\t\t\t{bet_counter:4}\t\t\t{tx_hash}")
            next_bet = bet_value[3]
        else:
            print("REKT : Bot exits")
            exit()

    return next_bet, loss_streak, bet_count


# Number of times, your bot will keep doing bets on the platfrom. It will stop if you have no balance to continue.
for _ in range(loops):
    if icx_balance >= bet:
        bet, loss_streak_counter, bet_counter = dice_bot(bet, loss_streak_counter, bet_counter)
    else:
        print("\nYou filled the treasury enough mate. Not enough icx...")
        break
else:
    print("\nDone!")
