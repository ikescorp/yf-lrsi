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
    data15 = tkr.history(period="7d", interval="1m")
    csvfile = "data/"+tkrid+"-"+datetime.now().strftime("%Y-%m-%d")+"-1m-7d.csv"
    print(csvfile)
    data15.to_csv(csvfile)
print("Stop - ", datetime.now())
