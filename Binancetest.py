
import datetime
import time
import math
from decimal import getcontext, Decimal, ROUND_DOWN
getcontext().prec = 6
from binance.client import Client
import configparser
import os

proDir = os.path.split(os.path.realpath(__file__))[0]
configPath = os.path.join(proDir, "Config.ini")
conf = configparser.ConfigParser()
# 讀取.ini檔案
conf.read(configPath)

# API資訊
api_key = conf.get('API','api_key')
api_secret = conf.get('API','api_secret')
client = Client(api_key=api_key, api_secret=api_secret)

x = 0

while True :

    ####基礎參數
    bid_depth = 20
    ask_depth = 20
    bid_price = 1.00001  #買單最高價格
    ask_price = 1.00045  #賣單最低價格
    refreshtime = 55

    ####1_清空場上所有訂單
    order = client.get_open_orders(symbol='WBTCBTC')

    time.sleep(0.2)

    for i in range(0, len(order), 1) :
        cancel = client.cancel_order(symbol='WBTCBTC', orderId=order[i]['orderId'])
        time.sleep(0.1)
    time.sleep(1)

    ####2_取得帳戶WBTC, BTC餘額, 並取到4位小數
    BTCbalance = client.get_asset_balance(asset='BTC')
    time.sleep(0.1)
    WBTCbalance = client.get_asset_balance(asset='WBTC')
    time.sleep(0.1)
    BTC = Decimal(BTCbalance['free']).quantize(Decimal('.0001'), rounding=ROUND_DOWN)
    WBTC = Decimal(WBTCbalance['free']).quantize(Decimal('.0001'), rounding=ROUND_DOWN)

    ####3_計算市場買賣單深度及掛單
    market_depth = client.get_order_book(symbol='WBTCBTC')
    all_bids = 0
    all_asks = 0

    if BTC > 0.0001 :
        for i in range(0, len(market_depth['bids']), 1) :
            bid = float(market_depth['bids'][i][1])
            all_bids = all_bids + bid
            if i == len(market_depth['bids']) :
                bid_price = Decimal(0.9500)
                bid_quantity = Decimal(Decimal(BTC) / Decimal(bid_price)).quantize(Decimal('.0001'), rounding=ROUND_DOWN)
                bid_order = client.order_limit_buy(symbol = 'WBTCBTC', quantity = bid_quantity, price = bid_price)
                print('流動性不足, 掛最低買價')
                break

            if all_bids >= bid_depth:
                if float(market_depth['bids'][i][0]) > bid_price:  #若市場最高買入價格高於最高買單價格, 則掛最高買價
                    bid_quantity = Decimal(Decimal(BTC) / Decimal(bid_price)).quantize(Decimal('.0001'), rounding=ROUND_DOWN)
                    bid_order = client.order_limit_buy(symbol = 'WBTCBTC', quantity = bid_quantity, price = bid_price)
                    break
                else:
                    bid_price = Decimal(market_depth['bids'][i][0]) + Decimal(0.00001)
                    bid_quantity = Decimal(Decimal(BTC) / Decimal(bid_price)).quantize(Decimal('.0001'), rounding=ROUND_DOWN)
                    bid_order = client.order_limit_buy(symbol = 'WBTCBTC', quantity = bid_quantity, price = bid_price)
                    break


    if WBTC > 0.0001 :
        for i in range(0, len(market_depth['asks']), 1) :
            ask = float(market_depth['asks'][i][1])
            all_asks = all_asks + ask
            if i == len(market_depth['asks']) :
                ask_price = Decimal(3.0000)
                ask_order = client.order_limit_sell(symbol = 'WBTCBTC', quantity = WBTC, price = ask_price)
                print('流動性不足, 掛最高賣價')
                break

            if all_asks >= ask_depth:
                if float(market_depth['asks'][i][0]) < ask_price:  #若市場最低賣出價格低於最低賣單價格, 則掛最低買價
                    ask_order = client.order_limit_sell(symbol = 'WBTCBTC', quantity = WBTC, price = ask_price)
                    break
                else:
                    ask_price = Decimal(market_depth['asks'][i][0]) - Decimal(0.00001)
                    ask_order = client.order_limit_sell(symbol = 'WBTCBTC', quantity = WBTC, price = ask_price)
                    break

    time.sleep(2)

    order_new = client.get_open_orders(symbol='WBTCBTC')
    time.sleep(1)
    for i in range(0, len(order_new), 1) :
        print(order_new[i]['side'] + ' ' + order_new[i]['symbol'] + ' ' + order_new[i]['price'] + ' ' + order_new[i]['origQty'])
    
    x = x + 1
    print('計數 : ', x )
    time.sleep(refreshtime)


    ######################################



    
