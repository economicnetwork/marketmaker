"""
feeder. polls exchanges and publishes
"""

from datetime import datetime

import archon.broker as broker
import archon.exchange.exchanges as exc
import archon.exchange.bitmex.bitmex as mex
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
import time
import redis
from topics import *


class Feeder(threading.Thread):
    
    def __init__(self, abroker):
        threading.Thread.__init__(self)
        setup_logger(logger_name="Feeder", log_file='feeder.log')
        self.log = logging.getLogger("Feeder")
        self.abroker = abroker
        self.log.info("init feeder")
        #r = redis.Redis(host='localhost', port=6379, db=0)
        self.redisclient = redis.StrictRedis(host='localhost', port=6379)  

        mex_sym = mex.instrument_btc_perp
        self.mex_sym = mex_sym

    def mex_get_book(self):
        market = models.market_from("XBT","USD")   
        smarket = models.conv_markets_to(market, exc.BITMEX) 
        #smarket = "XRPH19"
        book = self.abroker.afacade.get_orderbook(smarket, exc.BITMEX)
        return book

    def mex_position(self):
        mex_client = self.abroker.afacade.get_client(exc.BITMEX)
        pos = mex_client.position()
        return pos        

    def open_orders(self, e):
        if e==exc.BITMEX:
            oo = self.abroker.afacade.open_orders(exc.BITMEX)
            return oo     

    def run(self):
        while True:
            print ("feeder loop")
            #TODO openorders
            #TODO position

            data = self.mex_position()
            if data == []: data = "No position"
            print ("SUB_TOPIC_POS_MEX ",data)

            self.redisclient.publish(SUB_TOPIC_POS_MEX, json.dumps({"topic": SUB_TOPIC_POS_MEX,"data": data}))
            oo = self.open_orders(exc.BITMEX)
            print ("SUB_TOPIC_ORDERS_BITMEX " ,oo)
            self.redisclient.publish(SUB_TOPIC_ORDERS_BITMEX, json.dumps({"topic":SUB_TOPIC_ORDERS_BITMEX,"data":oo}))

            time.sleep(5)

if __name__=='__main__':    
    try:
        abroker = broker.Broker(setAuto=False)
        abroker.set_keys_exchange_file(exchanges=[exc.BITMEX]) 

        f = Feeder(abroker)
        f.start()
        f.join()
    except Exception as e:
        print (e)

    
        
