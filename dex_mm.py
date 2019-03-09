"""
market-maker strategy on 0x
production


"""

import archondex.relay.radar_public_api as radar_public
import archondex.relay.radar as radar
import archondex.binance_avg as binance
from archondex.ethplorer import get_balance
from tokens import *
from config_assets import asset_syms
from custom_logger import *
from archondex.abstract_marketmaker import Marketmaker

class StrategyMarketMaker(Marketmaker):

    def __init__(self):
        super().__init__()
        setup_logger(logger_name="StrategyMarketMaker", log_file='StrategyMarketMaker.log')
        self.logger = logging.getLogger("StrategyMarketMaker")

    def submit_all_buy_sell(self):
        self.logger.info("submit_all_buy_sell")
        #TODO check against existing orders
        #bal = get_balance(self.myaddr)        
        self.fetch_balances()
        
        zq = 0.01
        binance_band = 0.03
        target_bal_eth = 5
        for symbol in asset_syms[:]:
            sym_bal = self.balances[symbol]
            self.logger.info("%s %s"%(str(symbol),str(sym_bal)))
            pair = symbol + "-WETH"
            bin_avg_price = binance.get_average(symbol)
            self.logger.info("bin_avg_price %s"%str(bin_avg_price))
            max_bal = 1.5

            book = radar_public.orderbook(pair)
            topbid = float(book["bids"][0]['price'])
            topask = float(book["asks"][0]['price'])
            midprice = (topbid+topask)/2
            self.logger.info("best bid %s\t best ask %s\t midprice %s"%(str(topbid),str(topask),str(midprice)))
            
            bin_between = bin_avg_price > topbid and bin_avg_price < topask
            self.logger.info("bin_between %s"%str(bin_between))

            if bin_between:
                #pip = 0.0000001                
                target_bid = bin_avg_price * (1-zq)
                target_ask = bin_avg_price * (1+zq)

                target_bal_eth = 1
                bid_qty = round(target_bal_eth/target_bid,0)
                self.logger.info("BUY %s %10.8f %5.1f"%(symbol,target_bid,bid_qty))
                self.submit_buy(symbol, pair, target_bid, bid_qty)

                sym_bal = self.balances[symbol]
                eth_val = sym_bal * target_ask
                if eth_val > 0.1:
                    ask_qty = sym_bal * 0.9
                    self.logger.info("SELL %s %10.8f %5.1f"%(symbol,target_ask,ask_qty))
                    self.submit_sell(symbol, pair, target_ask, ask_qty)
                else:
                    self.logger.info("%s : not enough balance to sell"%symbol)




            #def submit_buy(self, symbol, pair, target_price, qty):
            """
            target_price = topbid + pip
            from_bin = target_price/bin_avg_price -1
            if from_bin > 0.03 or from_bin < -0.03:
                print ("out of band ")
                continue
            else:
                target_bal_eth = 0.1
                qty = round(target_bal_eth/target_price,0)
                print ("BUY ",symbol,":",target_price," ",qty)
                #self.submit_buy(symbol, pair, target_price, qty)
            #SELL
            sym_bal = self.balances[symbol]
            qty = sym_bal * 0.5
            print (symbol,sym_bal)
            target_price = topask - pip
            if from_bin > 0.03 or from_bin < -0.03:
                print ("out of band ")
                continue
            else:
                print ("SELL ",symbol,":",target_price," ",qty)
                pass
                #self.submit_sell(symbol, pair, target_price, qty)
            #self.submit_buy_band(symbol, pair, zq, bin_avg_price, binance_band, target_bal_eth, max_bal)
            #self.submit_sell_band(symbol, pair, zq, bin_avg_price, binance_band)
            """


    def submit_all_buy(self):
        #TODO check against existing orders
        #bal = get_balance(self.myaddr)        
        self.fetch_balances()
        
        zq = 0.01
        binance_band = 0.03
        target_bal_eth = 2
        for symbol in asset_syms[:1]:
            sym_bal = self.balances[symbol]
            print (symbol,sym_bal)
            pair = symbol + "-WETH"
            bin_avg_price = binance.get_average(symbol)
            max_bal = 1.5
            self.submit_buy_band(symbol, pair, zq, bin_avg_price, binance_band, target_bal_eth, max_bal)

    def submit_all_sell(self):
        #TODO check against existing orders
        #bal = get_balance(self.myaddr)        
        self.fetch_balances()
        
        zq = 0.01
        binance_band = 0.03
        target_bal_eth = 2
        for symbol in asset_syms[:]:
            sym_bal = self.balances[symbol]
            print (symbol,sym_bal)
            pair = symbol + "-WETH"
            bin_avg_price = binance.get_average(symbol)
            
            self.submit_sell_band(symbol, pair, zq, bin_avg_price, binance_band)

                                
                
def book():
    print ("get book")
    pair = "REP-WETH"
    radar_public.show_orderbook(pair)


if __name__=='__main__':
    s = StrategyMarketMaker()
    print (s)
    s.submit_all_buy_sell()
    #s.show_bal()
    #s.submit_all_buy()
    #s.submit_all_sell()