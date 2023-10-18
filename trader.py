import os
from typing import List

from alpaca.data import StockHistoricalDataClient, StockLatestQuoteRequest
from alpaca.trading import (
    TradingClient,
    MarketOrderRequest,
    OrderSide,
    TimeInForce,
    Position,
    TradeAccount,
)
from dotenv import load_dotenv

from logger import logger

load_dotenv()

api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")


class TradingBot:
    def __init__(self):
        self.stock_history_client = StockHistoricalDataClient(api_key, secret_key)
        self.trading_client = TradingClient(api_key, secret_key, paper=False)

    def get_latest_quote(self, symbol: str) -> float:
        request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        a = self.stock_history_client.get_stock_latest_quote(request)
        return a[symbol]

    def get_account(self) -> TradeAccount:
        account = self.trading_client.get_account()
        if account.account_blocked:
            raise ValueError("Account restricted for trading")
        return account

    def get_positions(self) -> List[Position]:
        return self.trading_client.get_all_positions()

    def sell_stock(self, symbol: str, qty: int = 1) -> None:
        self.get_account()
        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC,
        )
        self.trading_client.submit_order(request)
        logger.info("Successfully submitted sell request")

    def buy_stock(self, symbol: str, qty: int = 1) -> None:
        self.get_account()
        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC,
        )
        res = self.trading_client.submit_order(request)
        logger.info(f"Successfully submitted buy request: {res}")


if __name__ == "__main__":
    bot = TradingBot()
    print(bot.get_account())
