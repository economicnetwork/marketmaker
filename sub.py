"""
subscribes to feeder and sets
"""

import archon.config as config
from datetime import datetime

import archon.broker as broker
import archon.exchange.exchanges as exc
import archon.exchange.bitmex.bitmex as mex
import archon.exchange.bitmex.timeseries as timeseries
import archon.facade as facade
import archon.model.models as models
from archon.util import *

import redis
import time
import json
from feeder import *

from datetime import datetime

abroker = broker.Broker(setAuto=False)

def sub_print():
    
    redis_client = redis.Redis(host='localhost', port=6379)
    p = redis_client.pubsub()   
    p.subscribe(SUB_TOPIC_MARKET_BOOK_BITMEX)
    p.subscribe(SUB_TOPIC_POS_MEX)
    p.subscribe(SUB_TOPIC_ORDERS_BITMEX)
    while True:
        for data_raw in p.listen():
            if data_raw['type'] != "message":
                continue

            #refeed logic
            r = data_raw["data"]
            jd = json.loads(r)
            d = jd["data"]
            t = jd["topic"][4:]
            print (jd["topic"])
            #print (d)
            print ("set ",rep + t)
            redis_client.set(rep + t,json.dumps(d))

        time.sleep(0.1)

if __name__=='__main__':   
    sub_print()     
