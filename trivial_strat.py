#!/usr/bin/env python3

"""
trivial strategy 
"""

import archon.config as config
import traceback
from datetime import datetime

import archon.broker as broker
import archon.exchange.exchanges as exc
import archon.exchange.bitmex.bitmex as mex
import archon.exchange.bitmex.book_util as book_util
import archon.exchange.bitmex.timeseries as timeseries
import archon.facade as facade
import archon.model.models as models
from archon.custom_logger import setup_logger, remove_loggers
import archon.orders as orders
from archon.util import *   

import pandas as pd
import numpy

import time
import json
import atexit
import logging
import threading

from abc import ABC, abstractmethod    

from strat import Strategy
from topics import *

class TrivialStrategy(Strategy):

    def __init__(self, abroker, mex_sym):
        setup_logger(logger_name=__name__, log_file=__name__ + '.log')
        self.log = logging.getLogger(__name__)
        self.log.info('marb strategy')
        
        remove_loggers() 

        self.book_mex = None
        self.pos_qty = 0
        self.dif_wmid = 0

        self.order_qty = 5

        super().__init__(abroker, mex_sym)  

    def calc_mid(self, book):
        mb = book['bids'][0]
        ma = book['asks'][0]
        mid = (mb['price'] + ma['price'])/2
        return mid     

    def round_tick(self, price):
        rest = price % 1
        price_int = int(price)
        if rest > 0.5:
            return price_int + 0.5
        else:
            return price_int
        
    def calc_quotes(self):
        """ calculate one buy and sell quote
        trivial offset from bid and ask"""

        da = self.book['asks'][0]['price']
        db = self.book['bids'][0]['price']

        FV = self.calc_mid(self.book)

        buyorder = None
        sellorder = None
        
        oq = 3.0 #offset parameter in $

        qty = self.order_qty
        target_price = self.round_tick(FV - oq) # offset from mid
        order = [orders.ORDER_SIDE_BUY, qty, target_price]
        buyorder = order
        
        qty = self.order_qty            
        target_price = self.round_tick(FV + oq) # offset from mid
        order = [ orders.ORDER_SIDE_SELL, qty, target_price]
        sellorder = order

        return [buyorder, sellorder]

    def replace_order(self, old_order, new_order):
        self.cancel(old_order['orderId'])
        #self.submit_order(new_order)

    def handle_no_position(self):
        self.log.info("handle_no_position")
        target_orders = self.calc_quotes()
        self.log.info("target orders %s"%target_orders)
        #TODO adjust orders instead
        self.log.info("open orders %s"%str(self.oo))
        

        # if existing orders adjust orders by checking against targets
        if len(self.oo) > 0:
            buys = list(filter(lambda x: x['side']=='Buy', self.oo))
            sells = list(filter(lambda x: x['side']=='Sell', self.oo))

            [target_buyorder, target_sellorder] = target_orders

            for o in sells:
                self.log.info("check order %s"%str(o))
                dif = target_sellorder[2] - o['price']
                self.log.info("order dif %s"%str(dif))
                if dif >= 1:
                    self.log.info("price too low. cancel")
                    self.replace_order(o, target_sellorder)

                elif dif <= -1:
                    self.log.info("price too high. cancel")
                    self.replace_order(o, target_sellorder)
                    
                else:
                    self.log.info("price of existing order ok")

            for o in buys:
                self.log.info("check order %s"%str(o))
                dif = target_buyorder[2] - o['price']
                self.log.info("order dif %s"%str(dif))
                if dif >= 1:
                    self.log.info("price too low. cancel")
                    self.replace_order(o, target_buyorder)
                    
                elif dif <= -1:
                    self.log.info("price too high. cancel")
                    self.replace_order(o, target_buyorder)

                else:
                    self.log.info("price of existing order ok")

        else:
            # no existing orders - submit all
            for order in target_orders:
                #TODO cleanup order array to dict
                ttype = order[0]
                market = self.mex_sym
                qty = order[1]
                order_price = order[2]
                order = [market,ttype,order_price,qty]
                result = self.abroker.submit_order_post(order, exc.BITMEX)
                self.log.info("order result %s"%str(result))
                time.sleep(1)
           
    def handle_position(self):        
        #TODO same with skew
        return

    def handle_books(self, mexbook):
        self.log.info("handle books")
        db = self.abroker.get_db()
        db.books.insert_one({"orderbook":mexbook})  

        self.book = mexbook
        self.update_orders()

        book_util.display_book(self.book)

        got_max_position = False
        #TODO get position as int
        
        self.log.info("finished setting data")

        if len(self.oo)>4:
            self.log.info("too many orders")
            self.cancel_all()
            self.alive_flag = False
            return
        
        self.log.info("got_max_position %s"%str(got_max_position))

        if got_max_position:
            #self.handle_position()
            self.log.info("todo...")
            self.alive_flag = False
            return
            
        else:
            self.handle_no_position()
 
           

if __name__=='__main__':
    #todo register exit handler
    #atexit.register(clean_exit)
    
    try:
        abroker = broker.Broker(setAuto=False)
        abroker.set_keys_exchange_file(exchanges=[exc.BITMEX]) 
        mex_sym = mex.instrument_btc_perp
        #mex_sym = mex.instrument_btc_jun19
        strategy = TrivialStrategy(abroker, mex_sym)
        strategy.start()
        strategy.join()
    except Exception as e:
        traceback.print_exc()

    
        
