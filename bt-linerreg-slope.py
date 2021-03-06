from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime
import os.path
import sys
import backtrader as bt
import pandas as pd
from backtrader import Indicator
import numpy as np
from sklearn import linear_model

class LinearRegression(Indicator):
    alias = ('LR',)
    
    
    lines = ('linear_regression','ma')
    params = (
        ('len', 300),
    )
    iter = 0 

    def changeLen(self,length):
        self.params.len = length
        
    def next(self):
        if (self.iter > self.params.len):
            raw_prices = self.data.get(size=self.params.len)
            prices = np.array(raw_prices).reshape(-1, 1)
            x_line = np.array([i for i in range(0, self.params.len)]).reshape(-1, 1)
            # Create linear regression object
            regr = linear_model.LinearRegression()
            # Train the model using the training sets
            regr.fit(x_line, prices)
            prediction = regr.predict(np.array([self.params.len]).reshape(-1, 1))
            self.lines.linear_regression[0] = prediction
        self.iter += 1

class TestStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=15)
        self.rsi = bt.indicators.RelativeStrengthIndex()
        self.lrsi = bt.indicators.LaguerreRSI(self.dataclose,gamma=0.75 )
        self.linereg = LinearRegression(self.dataclose,len=20)

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
        #self.log('Close, %.2f' % self.dataclose[0])
        self.log('close : %s , linereg : %s' % (self.dataclose[0], self.linereg[0]))
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
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)
    cerebro.broker.setcommission(commission=0.001)



    datapath = 'IBULHSGFIN.NS'

    # Create a Data Feed
    data = bt.feeds.YahooFinanceData(
        dataname='IBULHSGFIN.NS'
        , name = 'IBULHSGFIN.NS'
        , fromdate = datetime.datetime(2018,12,1)
        , todate = datetime.datetime(2019,12,10)
        , reverse = False
        )
    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()