from datetime import datetime

import archon.broker as broker
import archon.exchange.exchanges as exc
import archon.exchange.bitmex.bitmex as mex
import archon.facade as facade
import archon.model.models as models
from archon.brokersrv.brokerservice import BrokerService

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
from archon.metrics import calc_mid_price
from archon.model import models
#from topics import *


if __name__=='__main__':    
    try:
        abroker = BrokerService(setAuto=True,initFeeder=False)
        abroker.set_keys_exchange_file(exchanges=[exc.BITMEX]) 
        book = abroker.orderbook(exc.BITMEX)
        book = models.conv_orderbook(book, exc.BITMEX)
        mid = calc_mid_price(book) 
        print ("bitmex mid",mid)
        
        pos = abroker.position(exc.BITMEX)
        #print (pos)
        print (pos[0]["currentQty"])

        #oo = abroker.openorders(exc.BITMEX)
        #print (oo)

    except Exception as e:
        print ("error ",e)

    
        
