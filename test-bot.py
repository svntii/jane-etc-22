#!/usr/bin/env python3
# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py --test prod-like; sleep 1; done

import argparse
from ast import ExceptHandler
from collections import deque
from enum import Enum
from pickle import GLOBAL
import time
import socket
import json



# ~~~~~============== CONFIGURATION  ==============~~~~~
# Replace "REPLACEME" with your team name!
team_name = "PRICKLYSCULPINS"
GLOBALID = 0         # ORDER ID is: unique order id
HOLDINGS = dict()
OPENORDER = dict()

HOLDINGS['bond'] = []
HOLDINGS['vale'] = []
HOLDINGS['valbz'] = []

OPENORDER['bond'] = []
OPENORDER['vale'] = []
OPENORDER['valbz'] = []


# ~~~~~============== MAIN LOOP ==============~~~~~

# You should put your code here! We provide some starter code as an example,
# but feel free to change/remove/edit/update any of it as you'd like. If you
# have any questions about the starter code, or what to do next, please ask us!
#
# To help you get started, the sample code below tries to buy BOND for a low
# price, and it prints the current prices for VALE every second. The sample
# code is intended to be a working example, but it needs some improvement
# before it will start making good trades!

# any bond value less than 1000 ---> buy
# if we have bonds worth less than buyer demand ---> sell [more than 1000]


def bond_buy(exchange, curr_price, curr_size):
    OPENORDER['bond'].append(GLOBALID)
    exchange.send_add_message(order_id=GLOBALID, symbol="BOND", dir=Dir.BUY,
                            price=curr_price, size=curr_size)  # SEND A BUY BOND FOR curr_price
    response = exchange.read_message()
    
    print(response)


def bond_sell(exchange, curr_price, curr_size):
    OPENORDER['bond'].append(GLOBALID)
    exchange.send_add_message(order_id=GLOBALID, symbol="BOND", dir=Dir.SELL,
                            price=curr_price, size=curr_size)  # SEND A SELL BOND FOR curr_price
    response = exchange.read_message()
    print(response)


def vale_buy(exchange, curr_price, curr_size):
    OPENORDER['vale'] += curr_size
    exchange.send_add_message(order_id=GLOBALID, symbol="VALE", dir=Dir.BUY,
                            price=curr_price, size=curr_size)  # SEND A BUY VALE FOR curr_price
    response = exchange.read_message()
    print(response)


def vale_sell(exchange, curr_price, curr_size):
    OPENORDER['vale'] -= curr_size
    exchange.send_add_message(order_id=GLOBALID, symbol="VALE", dir=Dir.SELL,
                            price=curr_price, size=curr_size)  # SEND A SELL VALE FOR curr_price
    response = exchange.read_message()
    print(response)

def valbz_buy(exchange, curr_price, curr_size):
    OPENORDER['valbz'] += curr_size
    exchange.send_add_message(order_id=GLOBALID, symbol="VALBZ", dir=Dir.BUY,
                            price=curr_price, size=curr_size)  # SEND A BUY VALE FOR curr_price
    response = exchange.read_message()
    print(response)


def valbz_sell(exchange, curr_price, curr_size):
    OPENORDER['valbz'] -= curr_size
    exchange.send_add_message(order_id=GLOBALID, symbol="VALBZ", dir=Dir.SELL,
                            price=curr_price, size=curr_size)  # SEND A SELL VALE FOR curr_price
    response = exchange.read_message()
    print(response)

def valbz_to_vale(exchange, curr_price, curr_size):
    if abs(len(OPENORDER['vale']) - len(HOLDINGS["vale"])) < 10:
    # vale_sell(exchange, curr_price, HOLDINGS['vale'])
        OPENORDER['valbz'] -= curr_size
        exchange.send_convert_message(order_id=GLOBALID, symbol= "VALBZ", dir=Dir.SELL, size=curr_size)  # SEND A SELL VALE FOR curr_price
        response = exchange.read_message()
        print(response)
    else:
        clear_open(exchange)

def clear_open(exchange):
    # this would cancel all open orders
    for orders,ids in OPENORDER.values():
        exchange.send_cancel_message(ids)
    print("all open orders done")


def vale_to_valbz(exchange, curr_price, curr_size):
    # valbz_sell(exchange, curr_price, HOLDINGS['valbz'])
    if abs(len(OPENORDER['valbz']) - len(HOLDINGS["valbz"])) < 10:
        OPENORDER['vale'] -= curr_size
        exchange.send_convert_message(order_id=GLOBALID, symbol= "VALE", dir=Dir.SELL, size=curr_size)  # SEND A SELL VALE FOR curr_price
        response = exchange.read_message()
        print(response)
    else:
        clear_open(exchange)


def val_check(exchange, curr_valbz, curr_vale, range_val):
    '''
        look at valbz
            find the book value of valbz
            check vale

            if BUY of vale is less than valbz -> BUY (RANGE)
            if SELL of vale > valbz -> SELL (RANGE)

            RANGE:

            if the spread is wide try to get the lowest vale, or highest val for sell
    '''
    print("print in here")
    # counter = 0
    # while counter < len(curr_valbz["buy"]) and curr_valbz["buy"][counter][0] > curr_vale["buy"][0][0]:
    #     vale_buy(exchange, curr_valbz["buy"][counter][0] - range_val, curr_vale["buy"][0][1]//2)
    #     counter += 1

    # counter = 0

    # while counter < len(curr_valbz["sell"]) and curr_valbz["sell"][counter][0] < curr_vale["sell"][0][0]:
    #     vale_buy(exchange, curr_valbz["sell"][counter][0] + range_val, curr_vale["sell"][0][1]//2)
    #     counter += 1

    if curr_valbz["sell"][0][0]+10 < curr_vale["buy"][0][0]:
        valbz_buy(exchange, curr_valbz["sell"][0][0] , 1)
        valbz_to_vale(exchange, curr_vale["buy"][0][0], 1)
        vale_sell(exchange, curr_vale["buy"][0][0] , 1)
    
    if curr_valbz["buy"][0][0]-10 > curr_vale["sell"][0][0]:
        vale_buy(exchange, curr_vale["sell"][0][0] - range_val, 1)
        vale_to_valbz(exchange, curr_valbz["buy"][0][0], 1)
        valbz_sell(exchange, curr_valbz["buy"][0][0] , 1)

def global_id_increment():
    global GLOBALID
    GLOBALID += 1


def book_bond_check(message, exchange):
    if message["symbol"] == "BOND":
        if message["sell"]:
            counter = 0
            while message["sell"][counter][0] < 1001:
                bond_buy(exchange, message["sell"][counter]
                        [0], message["sell"][counter][1]//2)
                counter += 1
        if message["buy"]:
            counter = 0
            while message["buy"][counter][0] >= 1000:
                bond_sell(exchange, message["buy"][counter]
                        [0], message["buy"][counter][1]//2)
                counter += 1


def main():
    args = parse_arguments()

    exchange = ExchangeConnection(args=args)  # create socket with the server

    # Store and print the "hello" message received from the exchange. This
    # contains useful information about your positions. Normally you start with
    # all positions at zero, but if you reconnect during a round, you might
    # have already bought/sold symbols and have non-zero positions.
    hello_message = exchange.read_message()
    print("First message from exchange:", hello_message)  # read in response

    # Send an order for BOND at a good price, but it is low enough that it is
    # unlikely it will be traded against. Maybe there is a better price to
    # pick? Also, you will need to send more orders over time.

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.BUY, price=999, size=1)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.BUY, price=998, size=1)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.BUY, price=997, size=1)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.BUY, price=999, size=3)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.BUY, price=999, size=5)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.BUY, price=999, size=10)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.BUY, price=999, size=25)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.BUY, price=999, size=50)  # TODO BOOK read

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.SELL, price=1001, size=1)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.SELL, price=1002, size=1)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.SELL, price=1003, size=1)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.SELL, price=1001, size=3)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.SELL, price=1001, size=5)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.SELL, price=1001, size=10)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.SELL, price=1001, size=25)  # TODO BOOK read
    # global_id_increment()

    # exchange.send_add_message(
    #     order_id=GLOBALID, symbol="BOND", dir=Dir.SELL, price=1001, size=50)  # TODO BOOK read
    # Set up some variables to track the bid and ask price of a symbol. Right
    # now this doesn't track much information, but it's enough to get a sense
    # of the VALE market.
    vale_bid_price, vale_ask_price = None, None  # TODO delete
    vale_last_print_time = time.time()  # TODO delete

    # Here is the main loop of the program. It will continue to read and
    # process messages in a loop until a "close" message is received. You
    # should write to code handle more types of messages (and not just print
    # the message). Feel free to modify any of the starter code below.
    #
    # Note: a common mistake people make is to call write_message() at least
    # once for every read_message() response.
    #
    # Every message sent to the exchange generates at least one response
    # message. Sending a message in response to every exchange message will
    # cause a feedback loop where your bot's messages will quickly be
    # rate-limited and ignored. Please, don't do that!
    vale = None
    valbz = None
    while True:

        message = exchange.read_message()

        # Some of the message types below happen infrequently and contain
        # important information to help you understand what your bot is doing,
        # so they are printed in full. We recommend not always printing every
        # message because it can be a lot of information to read. Instead, let
        # your code handle the messages and just print the information
        # important for you!
        if message["type"] == "close":
            print("The round has ended")
            break
        elif message["type"] == "error":
            print(message)
        elif message["type"] == "reject":
            print(message)
        elif message["type"] == "fill":
            print(message)
            if message["dir"] == 'buy':
                HOLDINGS[message['symbol']].append(message["order_id"])
                OPENORDER[message['symbol']] -= message['size']
            if message["dir"] == 'sell':
                HOLDINGS[message['symbol']] -= message['size']
                OPENORDER[message['symbol']] += message['size']
            # exchange.send_add_message(
            #     order_id=GLOBALID, symbol=message["symbol"], dir=message["dir"], price=message["price"], size=message["size"])  # TODO BOOK read
            # global_id_increment()
        elif message["type"] == "book":
            # print(message)
            if message["symbol"] == "VALBZ":
                valbz = message
            if message["symbol"] == "VALE":
                vale = message

                def best_price(side):
                    if message[side]:
                        return message[side][0][0]

                vale_bid_price = best_price("buy")
                vale_ask_price = best_price("sell")

                now = time.time()

                if now > vale_last_print_time + 1:
                    vale_last_print_time = now

                    # print(
                    #     {
                    #         "vale_bid_price": vale_bid_price,
                    #         "vale_ask_price": vale_ask_price,
                    #     }
                    # )
            if vale and valbz:
                # print('valcheck')
                val_check(exchange, valbz, vale, 5)

# ~~~~~============== PROVIDED CODE ==============~~~~~

# You probably don't need to edit anything below this line, but feel free to
# ask if you have any questions about what it is doing or how it works. If you
# do need to change anything below this line, please feel free to


class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ExchangeConnection:
    def __init__(self, args):
        self.message_timestamps = deque(maxlen=500)
        self.exchange_hostname = args.exchange_hostname
        self.port = args.port
        self.exchange_socket = self._connect(
            add_socket_timeout=args.add_socket_timeout)

        self._write_message({"type": "hello", "team": team_name.upper()})

    def read_message(self):
        """Read a single message from the exchange"""
        message = json.loads(self.exchange_socket.readline())
        if "dir" in message:
            message["dir"] = Dir(message["dir"])
        return message

    def send_add_message(
        self, order_id: int, symbol: str, dir: Dir, price: int, size: int
    ):
        """Add a new order"""
        global_id_increment()
        self._write_message(
            {
                "type": "add",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "price": price,
                "size": size,
            }
        )

    def send_convert_message(self, order_id: int, symbol: str, dir: Dir, size: int):
        """Convert between related symbols"""
        global_id_increment()
        self._write_message(
            {
                "type": "convert",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "size": size,
            }
        )

    def send_cancel_message(self, order_id: int):
        """Cancel an existing order"""
        self._write_message({"type": "cancel", "order_id": order_id})

    def _connect(self, add_socket_timeout):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if add_socket_timeout:
            # Automatically raise an exception if no data has been recieved for
            # multiple seconds. This should not be enabled on an "empty" test
            # exchange.
            s.settimeout(5)
        s.connect((self.exchange_hostname, self.port))
        return s.makefile("rw", 1)

    def _write_message(self, message):
        json.dump(message, self.exchange_socket)
        self.exchange_socket.write("\n")

        now = time.time()
        self.message_timestamps.append(now)
        if len(
            self.message_timestamps
        ) == self.message_timestamps.maxlen and self.message_timestamps[0] > (now - 1):
            print(
                "WARNING: You are sending messages too frequently. The exchange will start ignoring your messages. Make sure you are not sending a message in response to every exchange message."
            )


def parse_arguments():
    test_exchange_port_offsets = {"prod-like": 0, "slower": 1, "empty": 2}

    parser = argparse.ArgumentParser(description="Trade on an ETC exchange!")
    exchange_address_group = parser.add_mutually_exclusive_group(required=True)
    exchange_address_group.add_argument(
        "--production", action="store_true", help="Connect to the production exchange."
    )
    exchange_address_group.add_argument(
        "--test",
        type=str,
        choices=test_exchange_port_offsets.keys(),
        help="Connect to a test exchange.",
    )

    # Connect to a specific host. This is only intended to be used for debugging.
    exchange_address_group.add_argument(
        "--specific-address", type=str, metavar="HOST:PORT", help=argparse.SUPPRESS
    )

    args = parser.parse_args()
    args.add_socket_timeout = True

    if args.production:
        args.exchange_hostname = "production"
        args.port = 25000
    elif args.test:
        args.exchange_hostname = "test-exch-" + team_name
        args.port = 25000 + test_exchange_port_offsets[args.test]
        if args.test == "empty":
            args.add_socket_timeout = False
    elif args.specific_address:
        args.exchange_hostname, port = args.specific_address.split(":")
        args.port = int(port)

    return args


if __name__ == "__main__":
    # Check that [team_name] has been updated.
    assert (
        team_name != "REPLACEME"
    ), "Please put your team name in the variable [team_name]."

    main()
