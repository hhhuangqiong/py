from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from futu import *
import csv
import datetime
import backtrader as bt
import backtrader.feeds as btfeeds
import pandas

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)


ret, data, page_req_key = quote_ctx.request_history_kline('HK.00700', start='2021-03-11', end='2023-04-12', max_count=4000)  # 每页5个，请求第一页
if ret == RET_OK:
    print(data)
    print(type(data))
    data.to_csv('700.csv',index=None)
    print(data['code'][0])    # 取第一条的股票代码
    print(data['close'].values.tolist())   # 第一页收盘价转为 list
else:
    print('error:', data)
while page_req_key != None:  # 请求后面的所有结果
    print('*************************************')
    ret, data, page_req_key = quote_ctx.request_history_kline('HK.00700', start='2019-09-11', end='2023-04-12', max_count=2000, page_req_key=page_req_key) # 请求翻页后的数据
    if ret == RET_OK:
        print(data)
    else:
        print('error:', data)
print('All pages are finished!')

# dataframe = pandas.read_csv('700.csv')
# data = bt.feeds.PandasData(dataname=dataframe)