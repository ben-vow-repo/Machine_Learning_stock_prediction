import scaffolding as s

global_counter = s.Market()
global_counter.create_stocks()
global_counter.create_traders()

for g in range(10):
    for i in range(100):
        global_counter.new_day()
        for t in range(len(global_counter.all_traders)):
            for k in range(len(global_counter.all_stocks)):
                current_stock = global_counter.all_stocks[k]
                global_counter.all_traders[t].buy_stock(current_stock, global_counter)
            for k in range(len(global_counter.all_stocks)):
                current_stock = global_counter.all_stocks[k]
                if current_stock.id in global_counter.all_traders[t].portfolio:
                    global_counter.all_traders[t].sell_stock(current_stock,
                                                        global_counter.all_traders[t].portfolio[current_stock.id], global_counter)
                else:
                    continue
    global_counter.new_generation()

print(global_counter.ranked_traders[0].full_profit)

