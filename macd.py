# Python实用宝典
# 2020/04/20
# 转载请注明出处
import datetime
import os.path
import sys
import backtrader as bt
from backtrader.indicators import EMA


class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    @staticmethod
    def percent(today, yesterday):
        return float(today - yesterday) / today

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.volume = self.datas[0].volume

        self.order = None
        self.buyprice = None
        self.buycomm = None

        me1 = EMA(self.data, period=12)
        me2 = EMA(self.data, period=26)
        self.macd = me1 - me2 # 柱
        self.signal = EMA(self.macd, period=9) # 红线
        self.histo = self.macd - self.signal
        bt.indicators.MACDHisto(self.data)

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
                self.bar_executed_close = self.dataclose[0]
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    # Python 实用宝典
    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])
        if self.order:
            return

        if not self.position:
            condition1 = self.macd[-1] - self.signal[-1]
            condition2 = self.macd[0] - self.signal[0]
            if condition1 < 0 and condition2 > 0: #金叉
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()

        else:
            if self.histo < 0:
            # condition1 = self.macd[-1] - self.signal[-1]
            # condition2 = self.macd[0] - self.signal[0]
            # if condition1 > 0 and condition2 < 0: #金叉
            #     self.log('BUY CREATE, %.2f' % self.dataclose[0])
            #     self.order = self.buy()
            # condition = (self.dataclose[0] - self.bar_executed_close) / self.dataclose[0]
            # if condition > 0.1 or condition < -0.1:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()


if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.addstrategy(TestStrategy)

    # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, '603186.csv')

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

    cerebro.adddata(data)

    cerebro.broker.setcash(1000000)

    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    cerebro.broker.setcommission(commission=0.005)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot()