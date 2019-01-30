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
from topics import *


if __name__=='__main__':    
    try:
        abroker = BrokerService(setAuto=True)
        abroker.set_keys_exchange_file(exchanges=[exc.BITMEX]) 
        r = abroker.get_redis()
        print (r)
        time.sleep(10)
        book = abroker.get_orderbook(exc.BITMEX)
        print (book)

        #abroker = broker.Broker(setAuto=False)
        #abroker.set_keys_exchange_file(exchanges=[exc.BITMEX]) 

        #f = Feeder(abroker)
        #f.start()
        #f.join()
    except Exception as e:
        print (e)

    
        
