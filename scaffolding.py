from __future__ import annotations
import random
import statistics
import math

class Stocks:
    def __init__(self, id, chance_to_increase, demand_sensitivity):
        self.id = id
        self.current_price = 25
        self.chance_to_increase = chance_to_increase
        self.demand_sensitivity = demand_sensitivity
        self.amount_left = 100000
        self.price_history = []
        self.min_price = 10 # historial minimum for the stock, gives a suggested limit for the traders when to buy and sell
        self.max_price = 40 # historical maximum for the stock, gives a suggested limit for the traders when to buy and sell
        self.volatility = 0.2 # standard deviation of the stock price in history to show how likely the price is to change drastically
        self.shares_bought = 0
        self.shares_sold = 0
        self.firm_max = 200 # actual maximum for the stock price to reach
        self.firm_min = 1 # actual minimum for the stock price

    def direction_of_price(self):
        """decides the direction that the price will move using the chance of the stock increasing/decreasing and the current demand of the stock
        DOES NOT MOVE THE STOCK PRICE ITSELF, JUST A HELPER"""
        net_demand = self.shares_bought-self.shares_sold
        if self.shares_bought > 0 or self.shares_sold > 0:
            demand_ratio = net_demand/(self.shares_bought+self.shares_sold)
        else:
            demand_ratio = 0
        demand_adjustment = self.demand_sensitivity * demand_ratio
        probability = self.chance_to_increase + demand_adjustment
        increase_probability = max(0.05, min(0.95, probability))
        if random.random() < increase_probability:
            return True
        else:
            return False

    def volatility_change(self):
        """takes the standard deviation of the prices in the stock's history and applies it to the volatility, when price history
        too short for the stdev method it is auto applied to be 0.2"""
        if len(self.price_history) < 2:
            self.volatility = 0.2
            return self.volatility
        self.volatility = min(100,round(statistics.stdev(self.price_history),2))
        return self.volatility
    
    def stock_price_change(self, market: Market):
        """uses direction_of_price helper method to decide direction, randomly generates an amount to change the price
        of the stock by a random amount in a random range of the current value"""
        if self.direction_of_price():
            change = self.current_price * random.uniform(0,0.4)
            self.current_price = round((self.current_price + change),2)
            self.current_price = min(self.current_price, self.firm_max )

            if self.current_price > self.max_price:
                self.max_price = self.current_price
        else:
            change = self.current_price * random.uniform(-0.4,0)
            self.current_price = round(max(self.firm_min, (self.current_price + change)),2)
            if self.current_price < self.min_price:
                self.min_price = self.current_price
            
        market.stock_prices_over_time[market.current_day] = [market.all_stocks[self.id].current_price]
        self.price_history.append(self.current_price)
class Trader:
    def __init__(self, id ,minimum_buy_price, maximum_buy_price, minimum_sell_price, maximum_sell_price, risk_tolerance, cash_spend_percentage, total_sell_percentage, greediness):
        self.id = id
        self.cash_balance = 1000
        self.starting_balance = 1000
        self.portfolio_value = 0
        self.minimum_buy_price = minimum_buy_price # minimum price that the trader will buy at
        self.maximum_buy_price = maximum_buy_price # maximum price that the trader will buy at
        self.minimum_sell_price = minimum_sell_price # minimum price that the trader will sell at
        self.maximum_sell_price = maximum_sell_price # maxmimum price that the trader will sell at
        self.risk_tolerance = risk_tolerance # level of volatility that the trader will buy below
        self.cash_spend_percentage = cash_spend_percentage # percentage of trader's total balance that they are willing to spend on one buy
        self.total_sell_percentage = total_sell_percentage # percentage of trader's holdings of a stock that the trader is willing to sell at once
        self.profit_loss = 0
        self.transaction_history = []
        self.portfolio = {}
        self.greediness = greediness # how close to the historical maximum price of a stock that the trader will sell at
        self.full_profit = 0


    def sell_stock(self, stock: Stocks , holding: StocksBought, market: Market):
        """ defines whether or not a stock should be sold using the trader's min/max selling prices and the profit to be gained from the trade
        then completes the sale"""
        if stock.current_price < self.minimum_sell_price or stock.current_price > self.maximum_sell_price:
            return False
        selling_quantity = int(holding.quantity*self.total_sell_percentage)
        current_value = round(stock.current_price* selling_quantity, 2)
        original_cost = round(holding.price_bought_at* selling_quantity, 2)
        profit = current_value - original_cost

        if stock.current_price < stock.max_price*self.greediness or profit<0:
            return False

        if stock.volatility>99:
            working_volatility = stock.volatility%100

        if stock.volatility>0:
            working_volatility = int(float(str(stock.volatility)[:2]))

        if working_volatility > self.risk_tolerance:
            return False
        
        self.cash_balance += current_value
        self.profit_loss += profit

        stock.amount_left += selling_quantity
        stock.shares_sold += selling_quantity
        holding.quantity -= selling_quantity
        self.portfolio_value -= current_value

        if market.current_day not in market.transaction_log:
            market.transaction_log[market.current_day] = {}
        if self.id not in market.transaction_log[market.current_day]:
            market.transaction_log[market.current_day][self.id] = []
        market.transaction_log[market.current_day][self.id].append({
            'trader_id': self.id,
            'stock_id': stock.id,
            'action': ' sell',
            'price' : stock.current_price,
            'total_quantity': selling_quantity,
            'total_cost': selling_quantity*stock.current_price
        })
        
        



    def buy_stock(self, stock: Stocks, market: Market):
        """defines whether or not a stock should be bought using the trader's min/max selling price and the risk of purchasing the stock"""
        if stock.current_price < self.minimum_buy_price or stock.current_price > self.maximum_buy_price:
            return False

        if stock.volatility>0:
            working_volatility = int(float(str(stock.volatility)[:2]))

        if working_volatility > self.risk_tolerance:
            return False

        amount_spendable = self.cash_balance*self.cash_spend_percentage

        if amount_spendable < stock.current_price:
            return False
        if (
            not math.isfinite(self.cash_balance)
            or not math.isfinite(amount_spendable)
            or stock.current_price <= 0
        ):
            return False
        quantity = int(amount_spendable / stock.current_price)
        self.cash_balance -= quantity*stock.current_price
        self.portfolio_value += quantity*stock.current_price
        stock.amount_left -= quantity
        stock.shares_bought += quantity
        purchase = StocksBought(
            stock_id=stock.id,
            price_bought_at=stock.current_price,
            quantity=quantity,
            trader_id=self.id,
            day_bought=market.current_day
        )
        if stock.id not in self.portfolio:
            self.portfolio[stock.id] = purchase
            total_quantity = quantity
        else:
            holding = self.portfolio[stock.id]
            total_quantity = holding.quantity + quantity
            holding.price_bought_at = ((holding.quantity * holding.price_bought_at) + 
                                       (quantity*stock.current_price)) / total_quantity
            holding.quantity = total_quantity
        
        if market.current_day not in market.transaction_log:
            market.transaction_log[market.current_day] = {}
        if self.id not in market.transaction_log[market.current_day]:
            market.transaction_log[market.current_day][self.id] = []
        market.transaction_log[market.current_day][self.id].append({
            'trader_id': self.id,
            'stock_id': stock.id,
            'action': ' buy',
            'price' : stock.current_price,
            'total_quantity':total_quantity,
            'total_cost': total_quantity*stock.current_price
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
        self.ranked_traders = []

    def create_traders(self, amount_of_traders: int):
        """creates all base traders for the first generation"""
        for i in range(amount_of_traders):
            self.all_traders.append(Trader(i, random.randint(0,100), random.randint(100,200), random.randint(0,100), random.randint(100,200), 
                                           random.randint(0,100), random.randint(0,45)/100, random.randint(0,100)/100, random.randint(0,100)/100 ))

    def create_stocks(self, amount_of_stocks: int):
        """creates all stocks for each new generation"""
        self.all_stocks.clear()
        for i in range(amount_of_stocks):
            self.all_stocks.append(Stocks(i, random.randint(25,75)/100, random.randint(0,25)/100))
            self.stock_prices_over_time[0] = [self.all_stocks[i].current_price]

    def new_day(self):
        """moves day counter by one, resets stock stats, creates a new stock price"""
        self.current_day += 1
        for i in range(len(self.all_stocks)):
            current_stock = self.all_stocks[i]
            current_stock.stock_price_change(self)
            current_stock.shares_bought = 0
            current_stock.shares_sold = 0

    def final_worth(self):
        """gets the final value of each trader to sort by"""
        for i in range(len(self.all_traders)):
            self.all_traders[i].full_profit += (round(self.all_traders[i].portfolio_value, 2) 
            + round(self.all_traders[i].profit_loss, 2) + round(self.all_traders[i].cash_balance, 2))

    def evolution_sort(self):
        """sorts all traders by full profit"""
        self.ranked_traders = sorted(self.all_traders, 
                                     key = lambda trader: trader.full_profit, reverse=True)

    def mutate(self, amount_of_traders: int):
        """randomises a new generation based on the top 20% of the traders in the previous generation with it staying in a close range to the parent stat"""
        del self.ranked_traders[int(len(self.all_traders)*0.2):]
        self.all_traders.clear()
        for i in range(amount_of_traders):
            parent_trader = self.ranked_traders[random.randint(0,199)]
            new_min_buy = max(0, min(100, random.randint(parent_trader.minimum_buy_price-5, parent_trader.minimum_buy_price+5)))
            new_max_buy = max(100, min(200, random.randint(parent_trader.maximum_buy_price-5, parent_trader.maximum_buy_price+5)))
            new_min_sell = max(0, min(100, random.randint(parent_trader.minimum_sell_price-5, parent_trader.minimum_sell_price+5)))
            new_max_sell = max(100, min(200, random.randint(parent_trader.maximum_sell_price-5, parent_trader.maximum_sell_price+5)))
            new_risk_tolerance = max(0, min(100, random.randint(int((parent_trader.risk_tolerance*100)-15),int((parent_trader.risk_tolerance*100)+15))))/100
            new_cash_spend_percentage = max(0, min(100, random.randint(int((parent_trader.cash_spend_percentage*100)-15),int((parent_trader.cash_spend_percentage*100)+15))))/100
            new_total_sell_percentage = max(0, min(100, random.randint(int((parent_trader.total_sell_percentage*100)-15),int((parent_trader.total_sell_percentage*100)+15))))/100
            new_greediness = max(0, min(100, random.randint(int((parent_trader.greediness*100)-15),int((parent_trader.greediness*100)+15))))/100
            self.all_traders.append(Trader(i, new_min_buy, new_max_buy, new_min_sell, new_max_sell, new_risk_tolerance, new_cash_spend_percentage, new_total_sell_percentage, new_greediness))

    def new_generation(self, amount_of_traders:int, amount_of_stocks:int):
        """creates a new generation of traders and stocks"""
        self.final_worth()
        self.ranked_traders.clear()
        self.evolution_sort()
        self.mutate(amount_of_traders)
        self.all_stocks.clear()
        self.create_stocks(amount_of_stocks)
        self.stock_prices_over_time.clear()
        self.transaction_log.clear()
        self.current_day = 0
        top_trader = self.ranked_traders[0]
        print("GENERATION ROUNDUP\n" +
        "--------------------\n" +
        "Top final worth - " + str(round(top_trader.full_profit, 2)) +
        "\nPortfolio size - " + str(len(top_trader.portfolio)) +
        "\nProfit loss - " + str(round(top_trader.profit_loss, 2)) +
        "\nCash balance - " + str(round(top_trader.cash_balance, 2))
        )




