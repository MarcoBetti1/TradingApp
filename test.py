from datetime import timedelta, datetime
from pft import PortfolioTrade
from util import get_stock_data
from strategies import *
import matplotlib.pyplot as plt

def test_strategies(ticker_symbols, strategies, start, end):
    # Define your strategies
    # strategies = [
    #     create_day_based_strategy(0, 6),
    #     create_day_based_strategy(1, 5),
    #     create_day_based_strategy(2, 4),
    #     create_day_based_strategy(4, 2),
    #     create_day_based_strategy(5, 1),
    #     create_day_based_strategy(0, 6),
    #     create_day_based_strategy(3, 6),
    #     create_day_based_strategy(1, 6),
    #     create_day_based_strategy(2, 6),
    #     create_day_based_strategy(2, 3),
    #     create_day_based_strategy(3, 2),
    #     create_day_based_strategy(0, 4),
    #     create_day_based_strategy(4, 0),
    #     strategy_buy_and_hold# Buy on Wednesday, sell on Friday
    # ]

    for i, ticker_symbol in enumerate(ticker_symbols):
        # Get the stock data
        data = get_stock_data(ticker_symbol, start, end)

        values = []

        # Run and plot each strategy
        # Test each strategy
        for strategy in strategies:
            # Initialize the portfolio with a balance of $10000
            portfolio = PortfolioTrade()
            portfolio.start_balance(10000)

            # Execute the trading strategy
            portfolio_values = strategy(portfolio, data, ticker_symbol)
            stocks = {ticker_symbol:data.iloc[-1]}
            values.append(portfolio.get_profit(stocks))
            # Print the final balance of the portfolio
            #print(f'Final balance for {strategy.__name__} with {ticker_symbol}: {portfolio.get_portfolio_balance({ticker_symbol: data.iloc[-1]["Close"]})}')
            print(f'Final profit for {strategy.__name__} with {ticker_symbol}: {portfolio.get_profit(stocks)}')
            # Plot the portfolio balance over time
            plt.plot(data.index[1:], portfolio_values[1:], label=strategy.__name__)

        plt.xlabel('Date')
        plt.ylabel('Portfolio Value')
        plt.title(f'Portfolio Value Over Time for {ticker_symbol}')
        plt.legend()
        plt.show()
        #print(values)

    # Display all plots simultaneously


# Define the ticker symbols of the stocks to trade
#ticker_symbols = ["AAPL", "GOOG", "MSFT", "AMZN", "TSLA"]
ticker_symbols = ["SPY", "QQQ", "IWM", "PLTR","NFLX","TSM"]

start_date = '2024-06-06'
end_date = '2024-08-02'
# Define the strategies to test
#strategies = [strategy_fibonacci, strategy_buy_at_close_sell_at_open, strategy_buy_at_open_sell_at_close, strategy_buy_and_hold, strategy_sell_at_high_buy_at_low]
#strategy_buy_on_rise_sell_on_fall
strategies = [strategy_buy_on_low_volatility,strategy_buy_on_volume_increase,strategy_fibonacci_oscillate,strategy_buy_and_hold,strategy_local_extrema,strategy_optimized_buy_sell_periods,strategy_bollinger_bands,strategy_rsi_oversold_overbought,strategy_moving_average_crossover]
# Test the strategies on the ticker symbols
test_strategies(ticker_symbols, strategies, start_date, end_date)
