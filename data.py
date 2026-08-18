import random
class Stocks:
    def __init__(self, id, chance_to_increase, demand_sensitivity):
        self.id = id
        self.current_price = 25
        self.chance_to_increase = chance_to_increase
        self.demand_sensitivity = demand_sensitivity
        self.amount_left = 100000
        self.price_history = []
        self.min_price = 10
        self.max_price = 40
        self.volatility = 0.2
        self.shares_bought = 0
        self.shares_sold = 0

    def direction_of_price(self):
        net_demand = self.shares_bought-self.shares_sold
        demand_ratio = net_demand/(self.shares_bought+self.shares_sold)
        demand_adjustment = self.demand_sensitivity * demand_ratio
        probability = self.chance_to_increase + demand_adjustment
        increase_probability = max(0.05, min(0.95, probability))
        if random.random() < increase_probability:
            return True
        else:
            return False

    def volatility(self):
        









class Trader:
    def __init__(self, id ,minimum_buy_price, maximum_buy_price, minimum_sell_price, maximum_sell_price, risk_tolerance, cash_spend_percentage, total_sell_percentage, greediness):
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
        self.portfolio = []
        self.greediness = greediness


    def sell_stock(self, stock, holding, market):
        """ defines whether or not a stock should be sold using the trader's min/max selling prices and the profit to be gained from the trade"""
        if stock.current_price < self.minimum_sell_price or stock.current_price > self.maximum_sell_price:
            return False
        current_value = stock.current_price*holding.quantity
        original_cost = holding.price_bought_at*holding.quantity
        profit = original_cost - current_value

        if stock.current_price >= stock.max_price*self.greediness and profit>0:
            return True

        return False

    def buy_stock(self, stock, market):
        """defines whether or not a stock should be bought using the trader's min/max selling price and the risk of purchasing the stock"""
        if stock.current_price < self.minimum_buy_price or stock.current_price > self.maximum_buy_price:
            return False
        if stock.volatility > self.risk_tolerance:
            return False

        amount_spendable = self.cash_balance*self.cash_spend_percentage

        if amount_spendable < stock.current_price:
            return False

        quantity = int(amount_spendable / stock.current_price)
        self.cash_balance -= quantity*stock.current_price
        stock.amount_left -= quantity
        stock.shares_bought += quantity
        purchase = StocksBought(
            stock_id=stock.id,
            price_bought_at=stock.current_price,
            quantity=quantity,
            trader_id=self.id,
            day_bought=market.current_day
        )
        self.portfolio.append(purchase)
        if market.current_day not in market.transaction_log:
            market.transaction_log[market.current_day] = {}
        if self.id not in market.transaction_log[market.current_day]:
            market.transaction_log[market.current_day][self.id] = []
        market.transaction_log[market.current_day][self.id].append({
            'trader_id': self.id,
            'stock_id': stock.id,
            'action': ' buy',
            'price' : stock.current_price,
            'total_cost': quantity*stock.current_price
        })
        return True



class StocksBought:

    def __init__(self, stock_id, price_bought_at, quantity, trader_id, day_bought):
        self.stock_id = stock_id
        self.price_bought_at = price_bought_at
        self.quantity = quantity
        self.trader_id = trader_id
        self.day_bought = day_bought


class Market:
    def __init__(self):
        self.current_day = 0
        self.all_stocks = []
        self.all_traders = []
        self.transaction_log = {}
        self.stock_prices_over_time = {}
