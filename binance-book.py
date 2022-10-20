from operator import truediv
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.enums import *
from binance.exceptions import BinanceAPIException
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
import time

# Ключи binance
api_key = ""
api_secret = ""
client = Client(api_key, api_secret)
currency_pair = "BTCUSDT"

trend_sum = float(0)
difference_coefficient = float(4.0)
target_take_profit = float(30)
target_stop_loss = float(30)
minimum_book_bids_sum = float(500)
sale_stop_loss = int(0)
sale_take_profit = int(0)
buy = int(0)

status = True

while status:

    try:

        book_bids_sum = float(0)
        book_ask_sum = float(0)
        book_bids_index = 0
        book_ask_index = 0
        course_get_all_tickers = client.get_order_book(symbol=currency_pair, limit=1000)

        bids = True

        try:

            while bids:

                book_bids = course_get_all_tickers['bids'][book_bids_index]
                book_bids = float(book_bids[1])
                book_bids_sum += book_bids
                book_bids_index += 1

        except IndexError:
                        
                bids = False
                # print(book_bids_sum)

        ask = True

        try:

            while ask:

                book_ask = course_get_all_tickers['asks'][book_ask_index]
                book_ask = float(book_ask[1])
                book_ask_sum += book_ask
                book_ask_index += 1

        except IndexError:
                        
                ask = False
                # print(book_ask_sum)

        current_course = client.get_recent_trades(symbol=currency_pair)
        current_course = float(current_course[-1]['price'])
        # print(current_course)
        # print("-------------------")

        difference = book_bids_sum - book_ask_sum
        # print("Разница: ", str(difference))
        
        trend_sum += difference

        if trend_sum > 0:

            trend = "up"

        if trend_sum < 0:

            trend = "down"

        # print(trend)


        # Запись истории
        file = open("file.txt", "a")
        file.write("Bids: ")
        file.write(str(book_bids_sum))
        file.write(" Ask: ")
        file.write(str(book_ask_sum))
        file.write(" Difference: ")
        file.write(str(difference))
        file.write(" Trend: ")
        file.write(str(trend))
        file.write(" Course: ")
        file.write(str(current_course))
        file.write("\n")

        if book_bids_sum > book_ask_sum * difference_coefficient and trend == "up" and book_bids_sum > minimum_book_bids_sum:

            print("-------------------")
            print(current_course)
            print("Book_bids_sum: ", str(book_bids_sum))
            print("Book_ask_sum: ", str(book_ask_sum))
            print("Difference: ", str(difference))
            next_take_profit = current_course + target_take_profit
            print("Take_profit: ", str(next_take_profit))
            next_stop_loss = current_course - target_stop_loss
            print("Stop_loss: ", str(next_stop_loss))
            buy += 1
            print("Всего покупок: ", str(buy))

            rate = True
            
            while rate:

                current_course = client.get_recent_trades(symbol=currency_pair)
                current_course = float(current_course[-1]['price'])

                if current_course > next_take_profit:
                    
                    rate = False
                    print("-------------------")
                    print("Take_profit")
                    print("Курс: ", str(current_course))
                    sale_take_profit += 1
                    print("Всего Take_profit: ", str(sale_take_profit))
                    print("Всего Stop_loss: ", str(sale_stop_loss))
                
                if current_course < next_stop_loss:

                    rate = False
                    print("-------------------")
                    print("Stop_loss")
                    print("Курс: ", str(current_course))
                    sale_stop_loss += 1
                    print("Всего Take_profit: ", str(sale_take_profit))
                    print("Всего Stop_loss: ", str(sale_stop_loss))

    except BinanceAPIException as e:

        print("Ошибка: BinanceAPIException")
        time.sleep(3)

    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):

        print("Ошибка: ConnectTimeout")
        time.sleep(3)
