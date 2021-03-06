import backtrader as bt
import backtrader.feeds as btfeeds
import datetime

class Strategia(bt.Strategy):
    def log(self, txt, dt = None):
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s %s' %(dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
    def notifica_ordine(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        # Controlla se un ordine è stato completato
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('ORDINE CANCELLATO/MARGINE/RIFIUTATO')
        self.order = None

        
    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.dataclose[0])
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        # Check if we are in the market
        if not self.position:
            #Strategia
            #if self.dataclose[0] > 120:
                if self.dataclose[0] > self.dataclose[-1]:
                    if self.dataclose[-1] > self.dataclose[-2]:
                        self.log ('BUY CREATE, %.2f' % self.dataclose[0])
                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy()
        else:
            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                self.log ('SELL CREATE, %.2f' % self.dataclose[0])
            # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

class TestStrategy(bt.Strategy): #The one from the QuickStart Guide


    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
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

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] < self.dataclose[-1]:
                    # current close less than previous close

                    if self.dataclose[-1] < self.dataclose[-2]:
                        # previous close less than the previous close

                        # BUY, BUY, BUY!!! (with default parameters)
                        self.log('BUY CREATE, %.2f' % self.dataclose[0])

                        # Keep track of the created order to avoid a 2nd order
                        self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


    


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)
    
    nome ='extended_intraday_AAPL_1min_year1month1_adjusted.csv'
    da = datetime.datetime(2020, 8, 24, 4, 1, 00)
    a = datetime.datetime(2020, 9, 21, 20, 00, 00)
    
    data = btfeeds.YahooFinanceCSVData(
        dataname = nome,
        fromdate = da,
        todate = a,
        timeframe = bt.TimeFrame.Minutes,
        openinterest = -1,
        reverse = True
    )

    cerebro.adddata(data)
    cerebro.broker.setcash(100000.00)

    print('Saldo pre-trading: %.2f' %cerebro.broker.getvalue())
    cerebro.run()
    print('Saldo post-trading: %.2f' %cerebro.broker.getvalue())