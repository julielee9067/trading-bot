import os

from alpaca.data import StockHistoricalDataClient, StockLatestQuoteRequest
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")


class TradingBot:
    def __init__(self):
        self.client = StockHistoricalDataClient(api_key, secret_key)

    def get_latest_quote(self, stock_symbol: str) -> float:
        request = StockLatestQuoteRequest(symbol_or_symbols=stock_symbol)
        a = self.client.get_stock_latest_quote(request)

        return a[stock_symbol].ask_price


if __name__ == "__main__":
    bot = TradingBot()
    price = bot.get_latest_quote("SPY")
    print(price)
