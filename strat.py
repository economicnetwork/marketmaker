"""
abstract strategy
"""

import archon.config as config
import traceback
from datetime import datetime

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
import redis


#TODO 
#handle mex connection issues
#"message":"This request has expired - `expires` is in the past. C

class Strategy(threading.Thread):
    """ abstract strategy """

    def __init__(self, abroker, mex_sym):
        threading.Thread.__init__(self)
        setup_logger(logger_name="Strategy", log_file='strat.log')
        self.log = logging.getLogger("Strategy")
        self.abroker = abroker
        self.log.info("init strategy %s"%(mex_sym))

        self.mex_sym = mex_sym

        self.redis_client = redis.Redis(host='localhost', port=6379)

        self.alive_flag = True

    def mid_price(self, book):        
        topbid,topask = book['bids'][0],book['asks'][0]
        tbp,tap = topbid['price'],topask['price']
        mid = (tbp + tap)/2
        return mid
        
    
    def cancel_all(self):     
        oo = self.abroker.openorders(exc.BITMEX)
        self.log.info(oo)
        if oo:
            if len(oo)>0:
                for o in oo:
                    oid = o['orderID']
                    result = self.abroker.cancel_order(oid, exc.BITMEX)
                    self.log.info(result)
    
    def cancel_buys(self):
        oo = abroker.openorders(exc.BITMEX)
        print (oo) 
        buys = list(filter(lambda x: x['Side']=='Buy', oo))
        for o in buys:
            self.log.info("cancel %s"%str(o))
            oid = o['orderID']
            self.abroker.cancel_order(oid, exc.BITMEX)

    def cancel_sells(self):
        oo = abroker.openorders(exc.BITMEX)
        sells = list(filter(lambda x: x['side']=='Sell', oo))
        for o in sells:
            self.log.info("cancel %s"%str(o))
            oid = o['orderID']
            self.abroker.cancel_order(oid, exc.BITMEX)
    

    def buy_at_topbid(self):
        qty = self.order_qty
        target_price = self.book['bids'][0]['price']
        #self.abroker.buy(qty, target_price)

    def sell_at_topask(self, qty):
        #qty = self.order_qty
        target_price = self.book['asks'][0]['price']
        #self.abroker.submit(qty, target_price)

    def clean_exit(self):
        self.log.info("clean exit")
        #cancel_all()

    @abstractmethod
    def handle_position(self):
        pass

    @abstractmethod
    def handle_no_position(self):
        pass

    @abstractmethod
    def handle_books(self, mexbook):
        pass     

    def stop():
        self.alive_flag = False

    def run(self):
        """ main MM loop """
        self.log.info("run strategy")

        #TODO cancel all at startup
        #self.cancel_all()

        #TODO poll exeuctions
        #handle execution
        #handle orderfill


        while self.alive_flag:
            self.log.debug("loop")

            # main trade loop

            # TODO check pnl
            # stoploss
            print (type(self.abroker))
            oo = self.abroker.openorders(exc.BITMEX)
            self.log.info("oo %s"%str(oo))
            self.log.info("oolen  %i"%len(oo))

            if len(oo) > 2:
                #EXIT
                self.cancel_all()
                self.log.error("too many open orders")
                self.alive = False
                return
                #self.join()

            book = self.abroker.orderbook(exc.BITMEX)
            
            self.handle_books(book)

            
            #self.log.debug("book %s"%str(book))
            """
            self.log.info("mid price %s"%str(mid))
            
            if pos:
                pos_qty = pos['size']
            else:
                pos_qty = 0

            if pos_qty > 0:
                got_position = True

            if got_position:
                self.handle_position(mid, pos_qty)
            else:
                self.handle_no_position(mid)
            """
                
            #!TODO fix high wait time. this is because orders will not update fast enough
            time.sleep(3.0)
