from typing import Optional, Tuple

import schedule
from alpaca.trading import Position

from logger import logger
from trader import TradingBot

# Constants
DEFAULT_SYMBOL = "NRGU"
EASTERN_TIMEZONE = "US/Eastern"
MARKET_OPEN_TIME = "09:30"
MARKET_CLOSE_TIME = "15:58"


class Main:
    def __init__(self):
        self.bot = TradingBot()

    def run_sell(self, symbol: str = DEFAULT_SYMBOL) -> None:
        if not self.bot.is_market_open():
            logger.info("Market closed")
            return

        position, qty = self.find_position(symbol)
        if not position:
            logger.error(f"Can't sell {symbol} | qty: {qty}")
            return

        if self.should_sell(position):
            logger.info(f"Selling {symbol} | curr_price: {position.current_price}")
            self.bot.sell_stock(symbol, qty)

    def run_buy(self, symbol: str = DEFAULT_SYMBOL) -> None:
        if not self.bot.is_market_open():
            logger.info("Market closed")
            return

        if self.already_holding(symbol):
            logger.info(f"Already have {symbol}")
            return

        if self.bot.should_buy(symbol=symbol):
            logger.info(f"Buying stock: {symbol}")
            self.bot.buy_stock(symbol=symbol)

    def find_position(self, symbol: str) -> Tuple[Optional[Position], Optional[float]]:
        position = next((pos for pos in self.bot.get_positions() if pos.symbol == symbol), None)
        return (position, float(position.qty_available)) if position else (None, 0.0)

    def should_sell(self, position: Position) -> bool:
        last_closed_price = self.bot.get_last_closed_price(position.symbol)

        if position.current_price is None:
            logger.error(f"Cannot retrieve current price: {position.current_price}")
            return False

        return last_closed_price > float(position.current_price)

    def already_holding(self, symbol: str) -> bool:
        holding_stocks = {position.symbol for position in self.bot.get_positions()}
        return symbol in holding_stocks

    def main(self) -> None:
        schedule.every().day.at(MARKET_CLOSE_TIME).do(self.run_buy)
        schedule.every(10).seconds.until(MARKET_CLOSE_TIME).do(self.run_sell)
