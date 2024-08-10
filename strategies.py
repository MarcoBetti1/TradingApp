import pandas as pd
import copy
import time
from util import is_fibonacci
import numpy as np
from scipy.signal import argrelextrema

def strategy_buy_and_hold(portfolio, data, ticker_symbol):
    portfolio_values = []
    price = data.iloc[0]['Open']
    quantity = portfolio.balance // price
    portfolio.buy_stock(ticker_symbol, quantity, price)
    for i in range(0, len(data)):
        price = data.iloc[i]['Close']
        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))
    return portfolio_values

def trade_on_days(portfolio, data, ticker_symbol, buy_day, sell_day):
    portfolio_values = []
    for i in range(len(data)):
        price = data.iloc[i]['Close']
        if data.index[i].weekday() == buy_day:
            portfolio.buy_all(ticker_symbol, price)
        elif data.index[i].weekday() == sell_day:
            portfolio.sell_all(ticker_symbol, data.iloc[i]['Open'])
        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))
    return portfolio_values

def create_day_based_strategy(buy_day, sell_day):
    def custom_strategy(portfolio, data, ticker_symbol):
        return trade_on_days(portfolio, data, ticker_symbol, buy_day, sell_day)
    return custom_strategy

def strategy_buy_on_rise_sell_on_fall(portfolio, data, ticker_symbol):
    # Initialize portfolio_values with 1 initial balance
    portfolio_values = [portfolio.get_portfolio_balance({ticker_symbol: data.iloc[0]['Close']})]

    for i in range(1, len(data)):  # Start from the 1st day
        price = data.iloc[i-1]['Close']  # Use the closing price of the previous day
        quantity = portfolio.balance // price

        if i > 1 and data.iloc[i-1]['Close'] > data.iloc[i-2]['Close']:  # Price is rising
            portfolio.buy_stock(ticker_symbol, quantity, price)
        elif i > 1 and data.iloc[i-1]['Close'] < data.iloc[i-2]['Close']:  # Price is falling
            if portfolio.stocks.get(ticker_symbol, 0) > 0:
                price = data.iloc[i]['Open']  # Sell at the opening price of the current day
                quantity = portfolio.stocks.get(ticker_symbol, 0)
                portfolio.sell_stock(ticker_symbol, quantity, price)

        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))

    return portfolio_values

def strategy_buy_on_volume_increase(portfolio, data, ticker_symbol):
    # Initialize portfolio_values with 1 initial balance
    portfolio_values = [portfolio.get_portfolio_balance({ticker_symbol: data.iloc[0]['Close']})]

    for i in range(1, len(data)):
        price = data.iloc[i]['Close']
        quantity = portfolio.balance // price

        if data.iloc[i]['Volume'] > 1.5 * data.iloc[i-1]['Volume']:  # Volume increased significantly
            portfolio.buy_stock(ticker_symbol, quantity, price)
        else:
            if portfolio.stocks.get(ticker_symbol, 0) > 0:
                price = data.iloc[i]['Open']
                quantity = portfolio.stocks.get(ticker_symbol, 0)
                portfolio.sell_stock(ticker_symbol, quantity, price)

        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))

    return portfolio_values

def strategy_buy_on_low_volatility(portfolio, data, ticker_symbol):
    # Initialize portfolio_values with 5 initial balances
    portfolio_values = [portfolio.get_portfolio_balance({ticker_symbol: data.iloc[0]['Close']})] * 5

    for i in range(5, len(data)):  # Start from the 5th day to have enough data for volatility calculation
        price = data.iloc[i]['Close']
        quantity = portfolio.balance // price

        # Calculate the standard deviation of the closing prices for the past 5 days
        volatility = data.iloc[i-5:i]['Close'].std()

        # Calculate the average closing price for the past 5 days
        average_price = data.iloc[i-5:i]['Close'].mean()

        if volatility < 0.01 * average_price:  # Low volatility
            portfolio.buy_stock(ticker_symbol, quantity, price)
        else:
            if portfolio.stocks.get(ticker_symbol, 0) > 0:
                price = data.iloc[i]['Open']
                quantity = portfolio.stocks.get(ticker_symbol, 0)
                portfolio.sell_stock(ticker_symbol, quantity, price)

        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))

    return portfolio_values

def strategy_fibonacci(portfolio, data, ticker_symbol):
    portfolio_values = []
    a, b = 0, 1
    fib_day = 0
    buy = True

    for i in range(0, len(data)):
        price = data.iloc[i]['Close']
        quantity = portfolio.balance // price

        if i == fib_day:
            if buy:
                portfolio.buy_stock(ticker_symbol, quantity, price)
            else:
                if portfolio.stocks.get(ticker_symbol, 0) > 0:
                    price = data.iloc[i]['Open']
                    quantity = portfolio.stocks.get(ticker_symbol, 0)
                    portfolio.sell_stock(ticker_symbol, quantity, price)

            buy = not buy
            fib_day += b
            a, b = b, a + b

        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))

    return portfolio_values

def strategy_fibonacci_oscillate(portfolio, data, ticker_symbol):
    portfolio_values = []
    fib_sequence = [0, 1]
    while fib_sequence[-1] < len(data):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])

    buy = True
    for i in range(len(data)):
        price = data.iloc[i]['Close']
        quantity = portfolio.balance // price

        if i in fib_sequence:
            if buy:
                portfolio.buy_stock(ticker_symbol, quantity, price)
            else:
                if portfolio.stocks.get(ticker_symbol, 0) > 0:
                    price = data.iloc[i]['Open']
                    quantity = portfolio.stocks.get(ticker_symbol, 0)
                    portfolio.sell_stock(ticker_symbol, quantity, price)
            buy = not buy

        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))

    return portfolio_values

def strategy_moving_average_crossover(portfolio, data, ticker_symbol, short_window=10, long_window=50):
    portfolio_values = []
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['short_mavg'] = signals['price'].rolling(window=short_window, min_periods=1, center=False).mean()
    signals['long_mavg'] = signals['price'].rolling(window=long_window, min_periods=1, center=False).mean()
    signals['signal'] = np.where(signals['short_mavg'] > signals['long_mavg'], 1.0, 0.0)
    signals['positions'] = signals['signal'].diff()

    for i in range(len(data)):
        price = data.iloc[i]['Close']
        if signals['positions'].iloc[i] == 1:  # Buy signal
            quantity = portfolio.balance // price
            portfolio.buy_stock(ticker_symbol, quantity, price)
        elif signals['positions'].iloc[i] == -1:  # Sell signal
            quantity = portfolio.stocks.get(ticker_symbol, 0)
            portfolio.sell_stock(ticker_symbol, quantity, price)

        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))

    return portfolio_values

def strategy_rsi_oversold_overbought(portfolio, data, ticker_symbol, rsi_window=14, oversold=30, overbought=70):
    portfolio_values = []
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['returns'] = signals['price'].pct_change()
    signals['up_returns'] = np.where(signals['returns'] > 0, signals['returns'], 0)
    signals['down_returns'] = np.where(signals['returns'] < 0, -signals['returns'], 0)
    signals['avg_up'] = signals['up_returns'].rolling(window=rsi_window).mean()
    signals['avg_down'] = signals['down_returns'].rolling(window=rsi_window).mean()
    signals['rs'] = signals['avg_up'] / signals['avg_down']
    signals['rsi'] = 100.0 - (100.0 / (1.0 + signals['rs']))

    for i in range(len(data)):
        price = data.iloc[i]['Close']
        if signals['rsi'].iloc[i] < oversold:  # Oversold condition, buy
            quantity = portfolio.balance // price
            portfolio.buy_stock(ticker_symbol, quantity, price)
        elif signals['rsi'].iloc[i] > overbought:  # Overbought condition, sell
            quantity = portfolio.stocks.get(ticker_symbol, 0)
            portfolio.sell_stock(ticker_symbol, quantity, price)

        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))

    return portfolio_values

def strategy_bollinger_bands(portfolio, data, ticker_symbol, window=20, num_std=2):
    portfolio_values = []
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['rolling_mean'] = signals['price'].rolling(window=window).mean()
    signals['rolling_std'] = signals['price'].rolling(window=window).std()
    signals['upper_band'] = signals['rolling_mean'] + (signals['rolling_std'] * num_std)
    signals['lower_band'] = signals['rolling_mean'] - (signals['rolling_std'] * num_std)

    for i in range(len(data)):
        price = data.iloc[i]['Close']
        if price < signals['lower_band'].iloc[i]:  # Price below lower band, buy
            quantity = min(portfolio.balance // price, 100)  # Limit the quantity
            if quantity > 0:
                portfolio.buy_stock(ticker_symbol, quantity, price)
        elif price > signals['upper_band'].iloc[i]:  # Price above upper band, sell
            quantity = portfolio.stocks.get(ticker_symbol, 0)
            if quantity > 0:
                portfolio.sell_stock(ticker_symbol, quantity, price)

        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))

    return portfolio_values

def strategy_momentum_and_reversal(portfolio, data, ticker_symbol, momentum_window=5, reversal_window=20):
    portfolio_values = []
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['momentum'] = signals['price'].pct_change(periods=momentum_window)
    signals['reversal'] = signals['price'].pct_change(periods=reversal_window)

    for i in range(len(data)):
        price = data.iloc[i]['Close']
        if signals['momentum'].iloc[i] > 0 and signals['reversal'].iloc[i] < 0:  # Momentum up, long-term down - buy
            quantity = portfolio.balance // price
            portfolio.buy_stock(ticker_symbol, quantity, price)
        elif signals['momentum'].iloc[i] < 0 and signals['reversal'].iloc[i] > 0:  # Momentum down, long-term up - sell
            quantity = portfolio.stocks.get(ticker_symbol, 0)
            portfolio.sell_stock(ticker_symbol, quantity, price)

        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))

    return portfolio_values

def strategy_optimized_buy_sell_periods(portfolio, data, ticker_symbol, max_hold_days=10):
    def calculate_returns(buy_period, sell_period):
        portfolio_copy = copy.deepcopy(portfolio)
        for i in range(0, len(data), buy_period + sell_period):
            # Buy
            if i + buy_period < len(data):
                price = data.iloc[i]['Close']
                quantity = portfolio_copy.balance // price
                portfolio_copy.buy_stock(ticker_symbol, quantity, price)

            # Sell
            if i + buy_period + sell_period < len(data):
                price = data.iloc[i + buy_period + sell_period]['Close']
                quantity = portfolio_copy.stocks.get(ticker_symbol, 0)
                portfolio_copy.sell_stock(ticker_symbol, quantity, price)

        return portfolio_copy.balance

    best_returns = portfolio.balance
    best_buy_period = 1
    best_sell_period = 1

    for buy_period in range(1, max_hold_days):
        for sell_period in range(1, max_hold_days):
            returns = calculate_returns(buy_period, sell_period)
            if returns > best_returns:
                best_returns = returns
                best_buy_period = buy_period
                best_sell_period = sell_period

    # Now use the best periods to actually trade
    portfolio_values = [portfolio.get_portfolio_balance({ticker_symbol: data.iloc[0]['Close']})]
    for i in range(1, len(data)):
        price = data.iloc[i]['Close']

        if (i % (best_buy_period + best_sell_period)) < best_buy_period:
            # Buy period
            if portfolio.stocks.get(ticker_symbol, 0) == 0:
                quantity = portfolio.balance // price
                portfolio.buy_stock(ticker_symbol, quantity, price)
        else:
            # Sell period
            quantity = portfolio.stocks.get(ticker_symbol, 0)
            if quantity > 0:
                portfolio.sell_stock(ticker_symbol, quantity, price)

        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))

    return portfolio_values

def strategy_local_extrema(portfolio, data, ticker_symbol, window=10, confirmation_days=2, threshold_pct=0.02):
    portfolio_values = []

    # Initialize with the starting balance for the first window + confirmation days
    for _ in range(window + confirmation_days):
        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: data.iloc[0]['Close']}))

    for i in range(window + confirmation_days, len(data)):
        price = data.iloc[i]['Close']
        recent_prices = data.iloc[i-window-confirmation_days:i+1]['Close']

        is_min = recent_prices.iloc[:-confirmation_days].min() == recent_prices.iloc[window//2]
        is_max = recent_prices.iloc[:-confirmation_days].max() == recent_prices.iloc[window//2]

        avg_price = recent_prices.iloc[:-confirmation_days].mean()
        price_change = (price - avg_price) / avg_price

        if is_min and price_change < -threshold_pct:
            quantity = min(portfolio.balance // price, 100)
            if quantity > 0:
                portfolio.buy_stock(ticker_symbol, quantity, price)
        elif is_max and price_change > threshold_pct:
            quantity = portfolio.stocks.get(ticker_symbol, 0)
            if quantity > 0:
                portfolio.sell_stock(ticker_symbol, quantity, price)

        portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))

    return portfolio_values

# def strategy_sell_at_high_buy_at_low(portfolio, data, ticker_symbol):
#     portfolio_values = []
#     low = high = data.iloc[0]['Open']
#     portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: high}))
#     for i in range(1, len(data)):
#         price = data.iloc[i]['Close']
#         if price > high:
#             high = price
#             quantity = portfolio.stocks.get(ticker_symbol, 0)
#             portfolio.sell_stock(ticker_symbol, quantity, price)
#         elif price < low:
#             low = price
#             quantity = portfolio.balance // price
#             portfolio.buy_stock(ticker_symbol, quantity, price)
#         portfolio_values.append(portfolio.get_portfolio_balance({ticker_symbol: price}))
#     return portfolio_values
