from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import yfinance as yf

# Import the backtrader platform
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.datetime()
        print('%s, %s' % (dt.isoformat() , txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=9)
        self.rsi = bt.indicators.RelativeStrengthIndex()
        #rsi = self.sma
        self.lrsi = bt.indicators.LaguerreRSI(self.dataclose,gamma=0.75 )

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])
        print('lrsi: %.2f' % self.lrsi[0])
        if self.order:
            return

        if not self.position:
            if (self.lrsi[-1] < 0.2 and self.lrsi[0] > 0.2 ):
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy(size=100)

        else:
            #if (self.lrsi[0] > 70):
            if (self.lrsi[-1] > 0.8 and self.lrsi[0] < 0.8 ):
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell(size=100)


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../../datas/orcl-1995-2014.txt')
    tkrid = 'IBULHSGFIN.NS'
    tkr = yf.Ticker(tkrid)
    data15 = tkr.history(period="60d", interval="15m")
    data15.to_csv(tkrid)

    data = bt.feeds.GenericCSVData(
        dataname=tkrid,
        datetime=0,
        fromdate=datetime.datetime(2019, 11, 20),
        timeframe=bt.TimeFrame.Minutes,
        dtformat=('%Y-%m-%d %H:%M:%S+05:30'),
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1,
        reverse=True
        )
    #data.addfilter(bt.filters.HeikinAshi(data))
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    cerebro.datas
    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())