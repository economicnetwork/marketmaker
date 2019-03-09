from datetime import datetime

import archon.broker.broker as broker
import archon.exchange.exchanges as exc
import archon.exchange.bitmex.bitmex as mex
import archon.model.models as models
from archon.brokersrv.brokerservice import BrokerService
from archon.brokersrv.feeder import Feeder
from archon.util.custom_logger import setup_logger, remove_loggers
from archon.util import *   


if __name__=='__main__':    
    try:
        #setup service
        #this will init feeder to redis
        abroker = BrokerService(setAuto=True)        
        abroker.set_keys_exchange_file(exchanges=[exc.BITMEX]) 
        time.sleep(1)
        #r = abroker.get_redis()
        #print (r)
        
    except Exception as e:
        print (e)

    
        
