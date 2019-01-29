# makers

Simple market maker on bitmex

The strategy will act on data it got from feeder. It calculates the orders it wants to have open at any time and 
adjusts given the current open orders. Orders are submitted as post only

Simplifications

* only 1 order on each side
* Fair value is mid price
* ignores inventory i.e. the position
* no stoploss or any other risk measures

## links

* https://github.com/bitMEX/sample-market-maker
* https://github.com/makerdao/pymaker
