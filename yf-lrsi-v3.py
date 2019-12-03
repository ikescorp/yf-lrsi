import yfinance as yf
import pandas as pd
#import warnings
#import numpy as np
from datetime import datetime

ob = 0.80
os = 0.20
g = 0.75
tkrid_lst = pd.read_csv('yf-symbol-full.csv')
print("Start - ", datetime.now())

for tkrid in tkrid_lst['SYMBOL']:
    #print(datetime.now(), " | Processing | " , tkrid)
    tkr = yf.Ticker(tkrid)

    data15 = tkr.history(period="5d", interval="15m")
    data15 = data15.reset_index()
    
    data15['Close_HA'] = (
        data15['Open'] + data15['High'] + data15['Low'] + data15['Close']) / 4
    data15['Open_HA'] = (data15['Open'].shift() + data15['Close'].shift()) / 2
    data15['High_HA'] = data15[['Open', 'High', 'Close']].max(axis=1)
    data15['Low_HA'] = data15[['Open', 'Low', 'Close']].min(axis=1)

    #if data15['Open'][0] > 950:
    data15_len = data15.shape[0]
    data15['L0'], data15['L1'], data15['L2'], data15['L3'], data15[
        'CU'], data15['CD'], data15['rsi'], data15['lrsi'] = [
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        ]

    data15.loc[0, 'L0'] = ((1 - g) * data15.loc[0, 'Close_HA'])
    data15.loc[0, 'L1'] = (-g * data15.loc[0, 'L0'])
    data15.loc[0, 'L2'] = (-g * data15.loc[0, 'L0'])
    data15.loc[0, 'L3'] = (-g * data15.loc[0, 'L0'])
    for i in range(1, data15_len):
        data15.loc[i, 'L0'] = ((1 - g) * data15.loc[i, 'Close_HA']) + (
            g * data15.loc[i - 1, 'L0'])
        data15.loc[
            i, 'L1'] = (-g * data15.loc[i, 'L0']) + data15.loc[i - 1, 'L0'] + (
                g * data15.loc[i - 1, 'L1'])
        data15.loc[
            i, 'L2'] = (-g * data15.loc[i, 'L1']) + data15.loc[i - 1, 'L1'] + (
                g * data15.loc[i - 1, 'L2'])
        data15.loc[
            i, 'L3'] = (-g * data15.loc[i, 'L2']) + data15.loc[i - 1, 'L2'] + (
                g * data15.loc[i - 1, 'L3'])

        data15.loc[i, 'CU'] = ((
            (data15.loc[i, 'L0'] - data15.loc[i, 'L1'])
            if (data15.loc[i, 'L0'] > data15.loc[i, 'L1']) else 0) + (
                (data15.loc[i, 'L1'] - data15.loc[i, 'L2'])
                if (data15.loc[i, 'L1'] > data15.loc[i, 'L2']) else 0) + (
                    (data15.loc[i, 'L2'] - data15.loc[i, 'L3'])
                    if (data15.loc[i, 'L2'] > data15.loc[i, 'L3']) else 0))
        data15.loc[i, 'CD'] = ((
            (data15.loc[i, 'L1'] - data15.loc[i, 'L0'])
            if (data15.loc[i, 'L0'] < data15.loc[i, 'L1']) else 0) + (
                (data15.loc[i, 'L2'] - data15.loc[i, 'L1'])
                if (data15.loc[i, 'L1'] < data15.loc[i, 'L2']) else 0) + (
                    (data15.loc[i, 'L3'] - data15.loc[i, 'L2'])
                    if (data15.loc[i, 'L2'] < data15.loc[i, 'L3']) else 0))
        tempA = data15.loc[i, 'CU'] + data15.loc[i, 'CD']
        data15.loc[i, 'rsi'] = 0 if ((
            -1 if tempA == 0 else tempA) == -1) else (
                data15.loc[i, 'CU'] / (-1 if (tempA == 0) else tempA))
    data15['lrsi'] = pd.Series(data15['rsi']).ewm(span=2).mean()
    
    if (data15.loc[data15_len - 2, 'rsi'] < os
            and data15.loc[data15_len - 1, 'rsi'] > os):
        #print("Buy | ", tkrid  )
        print("Buy | ", tkrid, " | ", data15.loc[data15_len - 1, 'Datetime'])
    if (data15.loc[data15_len - 2, 'rsi'] > ob
            and data15.loc[data15_len - 1, 'rsi'] < ob):
        #print("Sell | "  , tkrid  )
        print("Sell | ", tkrid, " | ", data15.loc[data15_len - 1, 'Datetime'])
    #print(data15.tail(2))
print("Stop - ", datetime.now())
