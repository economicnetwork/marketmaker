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
        mtq = mb['quantity']+ma['quantity']
        mid = (mb['price'] + ma['price'])/2
        return mid
        
    """
    def cancel_buys(self):
        self.update_orders()        
        buys = list(filter(lambda x: x['direction']=='buy', self.oo))
        for o in buys:
            self.log.info("cancel %s"%str(o))
            self.cancel(o['orderId'])

    def cancel_sells(self):
        self.update_orders()
        sells = list(filter(lambda x: x['direction']=='sell', self.oo))
        for o in sells:
            self.log.info("cancel %s"%str(o))
            self.cancel(o['orderId'])
    """

    """
    def cancel_sells_min(self, min, max):
        self.update_orders()
        for o in self.oo:
            if o['direction'] == 'sell':
                p = o['price']
                
                self.cancel(o['orderId'])
    """
    

    def buy_at_topbid(self):
        qty = self.order_qty
        target_price = self.book['bids'][0]['price']
        #self.abroker.buy(qty, target_price)

    def sell_at_topask(self, qty):
        #qty = self.order_qty
        target_price = self.book['asks'][0]['price']
        #self.abroker.submit(qty, target_price)

    """
    def submit_order(self, order):
        self.log.info("submit_order %s"%str(order))
        #import pdb
        #pdb.set_trace()
        time.sleep(0.1)
        
        if order[0] == "BUY":
            self.buy(order[1],order[2])
        elif order[0] == "SELL":            
            self.sell(order[1],order[2])
    """
        
    def calc_quotes(self):
        """ calculate one buy and sell quote """
        da = self.book['asks'][0]['price']
        db = self.book['bids'][0]['price']

        buyorder = None
        sellorder = None
        
        qty = self.order_qty            
        target_price = da + 2.0
        order = ["SELL", qty, target_price]
        sellorder = order

        qty = self.order_qty
        target_price = db - 2.0
        order = ["BUY", qty, target_price]
        buyorder = order
        
        return [buyorder, sellorder]

    def replace_order(self, old_order, new_order):
        self.cancel(old_order['orderId'])
        #self.submit_order(new_order)

    def handle_no_position(self):
        self.log.info("handle_no_position")
        target_orders = self.calc_quotes()
        self.log.info("target orders %s"%target_orders)
        #TODO adjust orders instead
        

        # if existing orders adjust orders by checking against targets
        if len(self.oo) > 0:
            buys = list(filter(lambda x: x['direction']=='buy', self.oo))
            sells = list(filter(lambda x: x['direction']=='sell', self.oo))

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
                #self.submit_order(order)
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

    
        
