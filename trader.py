import os
from datetime import datetime, timedelta
from typing import List

import pytz  # type: ignore
from alpaca.data import (
    StockHistoricalDataClient,
    StockLatestQuoteRequest,
    TimeFrame,
    StockBarsRequest,
)
from alpaca.trading import (
    TradingClient,
    MarketOrderRequest,
    OrderSide,
    TimeInForce,
    Position,
    TradeAccount,
)
from dotenv import load_dotenv

from backtest.constants import LongWindowSize, ShortWindowSize
from logger import logger

load_dotenv()

api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")
est_timezone = pytz.timezone("US/Eastern")


class TradingBot:
    def __init__(self):
        self.stock_history_client = StockHistoricalDataClient(api_key, secret_key)
        self.trading_client = TradingClient(api_key, secret_key, paper=False)

    def get_latest_quote(self, symbol: str) -> float:
        request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        a = self.stock_history_client.get_stock_latest_bar(request)
        return a[symbol]

    def get_account(self) -> TradeAccount:
        account = self.trading_client.get_account()
        if account.account_blocked:
            raise ValueError("Account restricted for trading")
        return account

    def get_positions(self) -> List[Position]:
        return self.trading_client.get_all_positions()

    @staticmethod
    def get_today_open_price(symbol: str) -> float:
        bar = bot.stock_history_client.get_stock_bars(
            StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute,
                start=(datetime.today() - timedelta(days=1))
                .astimezone(est_timezone)
                .replace(hour=9, minute=29),
                end=(datetime.today() - timedelta(days=1))
                .astimezone(est_timezone)
                .replace(hour=9, minute=30),
            )
        )
        return bar.data[symbol][0].open

    # def get_current_price(self, symbol: str) -> float:
    #     # TODO: FIX THIS
    #     print(self.trading_client.get_open_position(symbol))

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

    def calculate_moving_average(self, window_size: int) -> float:
        bars = self.stock_history_client.get_stock_bars(
            StockBarsRequest(
                symbol_or_symbols="NRGU",
                timeframe=TimeFrame.Day,
                start=datetime.today().astimezone(est_timezone) - timedelta(days=60),
                end=datetime.today().astimezone(est_timezone) - timedelta(days=1),
            )
        ).data["NRGU"]

        total = 0.0

        for i in range(window_size):
            data = bars[len(bars) - i - 1]
            total += data.close

        return total / window_size

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

    def should_buy(self, symbol: str = "NRGU") -> bool:
        short_ma = self.calculate_moving_average(window_size=ShortWindowSize.NRGU.value)
        long_ma = self.calculate_moving_average(window_size=LongWindowSize.NRGU.value)
        logger.info(f"short_ma: {short_ma} | long_ma: {long_ma}")

        open_price = self.get_today_open_price(symbol)
        logger.info(f"open_price: {open_price} | current_price: ")

        return short_ma >= long_ma and 0 > open_price


if __name__ == "__main__":
    bot = TradingBot()

    # print(datetime.today().astimezone(est_timezone).replace(hour=9, minute=30))
    bars = bot.stock_history_client.get_stock_bars(
        StockBarsRequest(
            symbol_or_symbols="NRGU",
            timeframe=TimeFrame.Minute,
            start=(datetime.today() - timedelta(days=1))
            .astimezone(est_timezone)
            .replace(hour=9, minute=29),
            end=(datetime.today() - timedelta(days=1))
            .astimezone(est_timezone)
            .replace(hour=9, minute=31),
        )
    )
    print(bars.data["NRGU"])
