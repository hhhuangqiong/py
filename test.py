# import pandas as pd

# data = {
#   "calories": [420, 380, 390],
#   "duration": [50, 40, 45]
# }

# #load data into a DataFrame object:
# df = pd.DataFrame(data)

# print(df) 
# print(df.loc[0])
# print(df.loc[[0, 1]])

# df = pd.read_csv('data.csv')

# print(df) 
# import matplotlib.pyplot as plt
# import numpy as np

# xpoints = np.array([0, 6])
# ypoints = np.array([0, 250])

# plt.plot(xpoints, ypoints)
# plt.show()

# import backtrader as bt

# if __name__ == '__main__':

#     # 初始化模型
#     cerebro = bt.Cerebro()
#     # 设定初始资金
#     cerebro.broker.setcash(100000.0)

#     # 策略执行前的资金
#     print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

#     cerebro.run()

#     # 策略执行后的资金
#     print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

#     cerebro.broker.setcommission(0.005)
#     cerebro.addsizer(bt.sizers.FixedSize, stake=100)

# from futu import *
# quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

# ret, data = quote_ctx.get_capital_flow("HK.00700", period_type = PeriodType.INTRADAY)
# if ret == RET_OK:
#     print(data)
#     print(data['in_flow'][0])    # 取第一条的净流入的资金额度
#     print(data['in_flow'].values.tolist())   # 转为 list
# else:
#     print('error:', data)
# quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽

# # pip3 install matplotlib -i http://pypi.douban.com/simple/ --trusted-host pypi.douban.com

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
# from futu import *
import csv
import matplotlib
import datetime
import backtrader as bt
import backtrader.feeds as btfeeds
import pandas
import matplotlib.pyplot as plt
import numpy as np

# xpoints = np.array([0, 6])
# ypoints = np.array([0, 250])

# plt.plot(xpoints, ypoints)
# plt.show()

print(matplotlib.__version__)
# quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
# ret, data, page_req_key = quote_ctx.request_history_kline('HK.00700', start='2019-09-11', end='2019-10-18', max_count=30)  # 每页5个，请求第一页
# if ret == RET_OK:
#     print(data)
#     print(type(data))
#     # data.to_csv('700.csv',index=None)
#     print(data['code'][0])    # 取第一条的股票代码
#     print(data['close'].values.tolist())   # 第一页收盘价转为 list
# else:
#     print('error:', data)
# while page_req_key != None:  # 请求后面的所有结果
#     print('*************************************')
#     ret, data, page_req_key = quote_ctx.request_history_kline('HK.00700', start='2019-09-11', end='2019-10-18', max_count=30, page_req_key=page_req_key) # 请求翻页后的数据
#     if ret == RET_OK:
#         print(data)
#     else:
#         print('error:', data)
# print('All pages are finished!')

# dataframe = pandas.read_csv('700.csv')
# data = bt.feeds.PandasData(dataname=dataframe)


buy_time = 0
# 创建策略继承bt.Strategy 
class TestStrategy(bt.Strategy): 
    params = ( 
            # 持仓够5个单位就卖出  
            ('exitbars', 5), 
    )
    def log(self, txt, dt=None): 
        # 记录策略的执行日志  
        dt = dt or self.datas[0].datetime.date(0) 
        print('%s, %s' % (dt.isoformat(), txt)) 
    def __init__(self): 
        # 保存收盘价的引用  
        self.dataclose = self.datas[0].close 
        self.pe = self.datas[0].pe
        # 跟踪挂单  
        self.order = None
        # 买入价格和手续费  
        self.buyprice = None 
        self.buycomm = None

    # 订单状态通知，买入卖出都是下单  
    def notify_order(self, order): 
        if order.status in [order.Submitted, order.Accepted]: 
            # broker 提交/接受了，买/卖订单则什么都不做  
            return 

        # 检查一个订单是否完成  
        # 注意: 当资金不足时，broker会拒绝订单  
        if order.status in [order.Completed]: 
            if order.isbuy(): 
                self.log( 
                '已买入, 价格: %.2f, 费用: %.2f, 佣金 %.2f' % 
                (order.executed.price, 
                order.executed.value, 
                order.executed.comm)) 
                self.buyprice = order.executed.price 
                self.buycomm = order.executed.comm 
            elif order.issell(): 
                self.log('已卖出, 价格: %.2f, 费用: %.2f, 佣金 %.2f' % 
                (order.executed.price, 
                order.executed.value, 
                order.executed.comm)) 
            # 记录当前交易数量 
            print('当前持仓量', self.getposition(self.data).size) 
            print('当前持仓成本', self.getposition(self.data).price)
            self.bar_executed = len(self) 

        elif order.status in [order.Canceled, order.Margin, order.Rejected]: 
            self.log('订单取消/保证金不足/拒绝') 
 
        print('current Portfolio Value: %.2f' % cerebro.broker.getvalue())
        # 其他状态记录为：无挂起订单  
        self.order = None 


    # 交易状态通知，一买一卖算交易  
    def notify_trade(self, trade): 
        if not trade.isclosed: 
            return 
        self.log('交易利润, 毛利润 %.2f, 净利润 %.2f' % 
        (trade.pnl, trade.pnlcomm)) 

    def next(self): 
        # 记录收盘价  
        self.log('Close, %.2f' % self.dataclose[0]) 
        self.log('PE, %.2f' % self.pe[0]) 
        # 如果有订单正在挂起，不操作  
        if self.order: 
            return 

        # 如果没有持仓则买入  

        # 今天的收盘价 < 昨天收盘价  
        if self.dataclose[0] < self.dataclose[-1]: 
            # 昨天收盘价 < 前天的收盘价  
            if self.dataclose[-1] < self.dataclose[-2]: 
                    # 买入  
                    self.log('买入单, %.2f' % self.dataclose[0]) 
                    # 跟踪订单避免重复  
                    # 优化 增加数量，越低越加
                    self.order = self.buy() 

        if self.dataclose[0] > self.dataclose[-1]: 
            # 昨天收盘价 < 前天的收盘价  
            if self.dataclose[-1] > self.dataclose[-2]: 
                # 买入  
                if ((self.getposition(self.data).size > 0) ):
                    self.log('卖出单, %.2f' % self.dataclose[0]) 
                    # 跟踪订单避免重复  
                    self.order = self.sell() 

class GenericCSV_PE(bt.feeds.GenericCSVData):

    # Add a 'pe' line to the inherited ones from the base class
    lines = ('pe',)

    # openinterest in GenericCSVData has index 7 ... add 1
    # add the parameter to the parameters inherited from the base class
    params = (('pe', 6),)

data = GenericCSV_PE(
    dataname='700.csv',
    fromdate=datetime.datetime(2022, 1, 1),
    todate=datetime.datetime(2023, 4, 11),
     dtformat=('%Y-%m-%d %H:%M:%S'),
    datetime=1,
    open=2,
    high=4,
    low=5,
    close=3,
    volume=8
)

if __name__ == '__main__':
    # 策略开始
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy) 
    cerebro.adddata(data) 

    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.002)
    cerebro.addsizer(bt.sizers.FixedSize, stake=20)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    # cerebro.plot(style='bar')
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('Final Cash Value: %.2f' % cerebro.broker.get_cash())
    cerebro.plot()
    # quote_ctx.close() # 结束后记得关闭当条连接，防止连接条数用尽




