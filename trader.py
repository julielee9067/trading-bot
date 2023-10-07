import os

from alpaca.data import StockHistoricalDataClient, StockLatestQuoteRequest
from alpaca.trading import TradingClient, MarketOrderRequest, OrderSide, TimeInForce
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")


class TradingBot:
    def __init__(self):
        self.stock_history_client = StockHistoricalDataClient(api_key, secret_key)
        self.trading_client = TradingClient(api_key, secret_key, paper=True)

    def get_latest_quote(self, symbol: str) -> float:
        request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        a = self.stock_history_client.get_stock_latest_quote(request)

        return a[symbol].ask_price

    def verify_account_status(self) -> None:
        if self.trading_client.get_account().account_blocked:
            raise ValueError("Account restricted for trading")

    def sell_stock(self, symbol: str) -> None:
        self.verify_account_status()
        request = MarketOrderRequest(
            symbol=symbol,
            qty=1,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        self.trading_client.submit_order(request)
        print("Successfully submitted sell request")

    def buy_stock(self, symbol: str) -> None:
        self.verify_account_status()
        request = MarketOrderRequest(
            symbol=symbol,
            qty=1,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        self.trading_client.submit_order(request)
        print("Successfully submitted buy request")


if __name__ == "__main__":
    bot = TradingBot()
    price = bot.get_latest_quote("SPY")
    print(price)