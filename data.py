class Stocks:
    def __init__(self, id, chance_to_increase, chance_to_decrease):
        self.id = id
        self.current_price = 25
        self.chance_to_increase = chance_to_increase
        self.chance_to_decrease = chance_to_decrease
        self.amount_left = 10000
        self.price_history = []
        self.min_price = 10
        self.max_price = 40
        self.volatility = 0.2


class Trader:
    def __init__(self, id ,minimum_buy_price, maximum_buy_price, minimum_sell_price, maximum_sell_price, risk_tolerance, cash_spend_percentage, total_sell_percentage):
        self.id = id
        self.cash_balance = 1000
        self.starting_balance = 1000
        self.portfolio_value = 0
        self.minimum_buy_price = minimum_buy_price
        self.maximum_buy_price = maximum_buy_price
        self.minimum_sell_price = minimum_sell_price
        self.maximum_sell_price = maximum_sell_price
        self.risk_tolerance = risk_tolerance
        self.cash_spend_percentage = cash_spend_percentage
        self.total_sell_percentage = total_sell_percentage
        self.profit_loss = 0
        self.transaction_history = []




class Stocks_bought:
    def __init__(self, id, price_bought_at, quantity, trader_id):
        self.id = id
        self.price_bought_at = price_bought_at
        self.quantity = quantity
        self.trader_id = trader_id

class Market:
    def __init__(self):
        self.current_day = 0
        self.all_stocks = []
        self.all_traders = []
        self.transaction_log = []
        self.stock_prices_over_time = {}
