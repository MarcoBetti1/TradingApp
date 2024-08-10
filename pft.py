#THIS is the portfolio trade class. We want to build a framework that this may eventually make smart disisions on what to buy and sell. for now it will be set to buy and sell at a fixed time every day
# The class will store either the balance when it sells the stock, or the stock when it buys it. we may also want to make it store trade or balance history.
# the class will also have a function that will return the current balance of the portfolio. This is calculated by (total cash) + (stock price * stock amount)...
# since it may have different stocks at one time, we will have to store that strategically, possibly using the Ticer symbol as a key in a dictionary.

# we will also need rules so that it cannot buy stock it cannot afford, and cannot sell stock it does not have.

# we want this to be modular, so we can implement it in a sense and compare different strategies

class PortfolioTrade:
    def __init__(self):
        # Initialize the portfolio with an empty dictionary for stocks and 0 balance
        self.stocks = {}  # Dictionary to store stocks. Key: Ticker Symbol, Value: Quantity
        self.balance = 0  # Total cash balance
        self.start_bal = 0

    def start_balance(self,amount):
        self.balance = amount
        self.start_bal = amount
    def buy_stock(self, ticker_symbol, quantity, price):
        # Check if the portfolio can afford the purchase
        if self.balance < price * quantity:
            print("Cannot afford to buy the stock")
            return
        # Deduct the cost from the balance and add the stock to the portfolio
        self.balance -= price * quantity
        if ticker_symbol in self.stocks:
            self.stocks[ticker_symbol] += quantity
        else:
            self.stocks[ticker_symbol] = quantity

    def sell_stock(self, ticker_symbol, quantity, price):
        # Check if the portfolio has the stock to sell
        if ticker_symbol not in self.stocks or self.stocks[ticker_symbol] < quantity:
            print("Cannot sell stock that the portfolio does not have")
            return
        # Add the proceeds to the balance and remove the stock from the portfolio
        self.balance += price * quantity
        self.stocks[ticker_symbol] -= quantity
        if self.stocks[ticker_symbol] == 0:
            del self.stocks[ticker_symbol]

    def get_portfolio_balance(self, stock_prices):
        # Calculate the total balance of the portfolio
        total_balance = self.balance
        for ticker_symbol, quantity in self.stocks.items():
            total_balance += stock_prices[ticker_symbol] * quantity
        return total_balance

    def buy_all(self, ticker_symbol, price):
        quantity = self.balance // price
        self.buy_stock(ticker_symbol, quantity, price)

    def sell_all(self, ticker_symbol, price):
        quantity = self.stocks.get(ticker_symbol, 0)
        self.sell_stock(ticker_symbol, quantity, price)
    def get_profit(self, stock_prices):
        # Calculate the total balance of the portfolio
        total_balance = self.balance
        for ticker_symbol, quantity in self.stocks.items():
            total_balance += stock_prices[ticker_symbol] * quantity
        return total_balance-self.start_bal
