#!/usr/bin/env python3

"""
trivial strategy 
"""

import archon.config as config
import traceback
from datetime import datetime

#import archon.broker as broker
from archon.brokersrv.brokerservice import BrokerService
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

class TrivialStrategy(Strategy):

    def __init__(self, abroker, mex_sym, order_qty, zoff):
        setup_logger(logger_name=__name__, log_file=__name__ + '.log')
        self.log = logging.getLogger(__name__)
        self.log.info('marb strategy')
        
        remove_loggers() 

        # init data
        self.book_mex = None
        self.pos_qty = 0

        self.zoff = zoff # the offset in $
        self.diff_cancel = 1.0 # cancel if diff is larger than this
        self.order_qty = order_qty

        super().__init__(abroker, mex_sym)  

    def calc_mid(self, book):
        print (book)
        bids = list(filter(lambda x: x['side']=='Buy', book))
        asks = list(filter(lambda x: x['side']=='Sell', book))
        print (">>>> " ,bids[0])
        #, asks)
        mb = bids[0]
        ma = asks[0]
        mid = (mb['price'] + ma['price'])/2
        return mid     

    def round_tick(self, price):
        """ round to bitmex tick size of 0.50$ """
        ip = round(price,0)
        if ip > price: ip=ip-1
        rest = price - ip
        r = -1             
        if rest > 0.5 and rest <= 0.75:
            r = ip + 0.5
        elif rest > 0.75:
            r = ip
        elif rest <= 0.5:
            r = ip
        return r

        
    def calc_quotes(self):
        """ calculate one buy and sell quote
        trivial offset from bid and ask"""

        bids = list(filter(lambda x: x['side']=='Buy', self.book))
        asks = list(filter(lambda x: x['side']=='Sell', self.book))
        da = asks[0]['price']
        db = bids[0]['price']

        FV = self.calc_mid(self.book)

        buyorder = None
        sellorder = None
        
        oq = self.zoff #offset parameter in $

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
        oid = old_order['orderID']
        result = self.abroker.cancel_order(oid, exc.BITMEX)
        return result
        #self.submit_order(new_order)

    def order_str(self, o):
        s = "%s %5.3f %5.3f"%(o['side'],o['orderQty'],o['price'])
        return s

    def handle_no_position(self):
        self.log.info("handle_no_position")
        target_orders = self.calc_quotes()
        self.log.info("target orders %s"%target_orders)
        #TODO adjust orders instead
        oo = abroker.openorders(exc.BITMEX)
        self.log.info("open orders %s"%str(oo))
        
        buys = list(filter(lambda x: x['side']=='Buy', oo))
        sells = list(filter(lambda x: x['side']=='Sell', oo))
        [target_buyorder, target_sellorder] = target_orders

        # if existing orders adjust orders by checking against targets
        
        if len(buys) > 0:
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
        
        if len(sells) > 0:
            for o in sells:
                self.log.info("check order %s"%self.order_str(o))
                dif = target_sellorder[2] - o['price']
                self.log.info("order dif %s"%str(dif))
                if dif >= self.diff_cancel:
                    self.log.info("price too low. cancel")
                    self.replace_order(o, target_sellorder)

                elif dif <= -self.diff_cancel:
                    self.log.info("price too high. cancel")
                    self.replace_order(o, target_sellorder)
                    
                else:
                    self.log.info("price of existing order ok")

                
        if len(buys) == 0:
            for order in [target_buyorder]:
                #TODO cleanup order array to dict
                ttype = order[0]
                market = self.mex_sym
                qty = order[1]
                order_price = order[2]
                order = [market,ttype,order_price,qty]
                result = self.abroker.submit_order_post(order, exc.BITMEX)
                self.log.info("order result %s"%str(result))
                time.sleep(1)


        if len(sells) == 0:
            for order in [target_sellorder] :
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
        #db = self.abroker.get_db()
        #db.books.insert_one({"orderbook":mexbook})  

        self.book = mexbook
        #self.update_orders()

        #book_util.display_book(self.book)
        mid = self.calc_mid(self.book)
        self.log.info("mid price %s"%str(mid))

        pos = abroker.position(exc.BITMEX)
        self.pos_qty = int(pos[0]['currentQty'])
        
        got_max_position = self.pos_qty > 50
        oo = abroker.openorders(exc.BITMEX)
        self.log.info("finished setting data")

        if len(oo)>4:
            self.log.info("too many orders")
            #self.cancel_all()
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
        #assume service is running, this is just a proxy
        abroker = BrokerService(setAuto=True,initFeeder=False)
        abroker.set_keys_exchange_file(exchanges=[exc.BITMEX])
        mex_sym = mex.instrument_btc_perp
        zoff = 1.0
        order_qty = 1.0
        strategy = TrivialStrategy(abroker, mex_sym, order_qty, zoff)
        strategy.start()
        strategy.join()
    except Exception as e:
        traceback.print_exc()

    
        
