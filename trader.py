import os
from datetime import datetime, timedelta
from typing import List

import pytz  # type: ignore
import yfinance
from alpaca.data import (
    StockHistoricalDataClient,
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
        self.trading_client = TradingClient(api_key, secret_key, paper=True)

    def is_market_open(self) -> bool:
        clock = self.trading_client.get_clock()
        return clock.is_open

    def get_account(self) -> TradeAccount:
        account = self.trading_client.get_account()
        if account.account_blocked:
            raise ValueError("Account restricted for trading")
        return account

    def get_positions(self) -> List[Position]:
        return self.trading_client.get_all_positions()

    @staticmethod
    def get_today_open_price(symbol: str) -> float:
        ticker = yfinance.Ticker(symbol)
        data = ticker.history(period="1d")
        return round(data["Open"][0], 2)

    # TODO: check when market is actually open
    @staticmethod
    def get_last_closed_price(symbol: str) -> float:
        ticker = yfinance.Ticker(symbol)
        data = ticker.history(period="5d")
        print(data["Close"])
        return round(data["Close"][-2], 2)

    @staticmethod
    def get_current_price(symbol: str) -> float:
        ticker = yfinance.Ticker(symbol)
        data = ticker.history(period="1d")
        return round(data["Close"][0], 2)

    def sell_stock(self, symbol: str, qty: float = 1) -> None:
        self.get_account()
        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC,
        )
        self.trading_client.submit_order(request)
        logger.info("Successfully submitted sell request")

    def calculate_moving_average(self, symbol: str, window_size: int) -> float:
        bars = self.stock_history_client.get_stock_bars(
            StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=datetime.today().astimezone(est_timezone) - timedelta(days=60),
                end=datetime.today().astimezone(est_timezone) - timedelta(days=1),
            )
        ).data[symbol]

        total = 0.0

        for i in range(window_size):
            data = bars[len(bars) - i - 1]
            total += data.close

        return total / window_size

    def buy_stock(self, symbol: str) -> None:
        balance = self.get_account().cash
        if not balance:
            logger.error(f"Not enough balance: {balance}")
            return

        curr_price = self.get_current_price(symbol)

        # Buy as much as we can with left over cash in the account
        qty = balance // curr_price  # type: ignore
        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC,
        )
        res = self.trading_client.submit_order(request)
        logger.info(f"Successfully submitted buy request: {res} | curr_price: {curr_price}")

    def should_buy(self, symbol: str = "NRGU") -> bool:
        short_ma = self.calculate_moving_average(
            window_size=ShortWindowSize.NRGU.value, symbol=symbol
        )
        long_ma = self.calculate_moving_average(
            window_size=LongWindowSize.NRGU.value, symbol=symbol
        )
        logger.info(f"short_ma: {short_ma} | long_ma: {long_ma}")

        open_price = self.get_today_open_price(symbol)
        curr_price = self.get_current_price(symbol)
        logger.info(f"open_price: {open_price} | current_price: {curr_price}")

        return short_ma >= long_ma and curr_price > open_price


if __name__ == "__main__":
    bot = TradingBot()

    print(bot.get_last_closed_price("NRGU"))

"""
전 날 close price (stop loss price)
2분마다 가격 체크
가격이 stop loss 보다 낮으면 market sell

market 닫기 2분 전
오늘 open 보다 지금 가격이 더 높으면 market buy

1. 현재 주식 정확한 가격 체크  DONE
2. 오늘 오픈가 체크  DONE
3. 마켓 sell & buy order  DONE
4. 어제 close price  DONE
5. market status  DONE

6. Schedule 작성  TODO
7. alpaca vs yfinance 비교  TODO
"""
