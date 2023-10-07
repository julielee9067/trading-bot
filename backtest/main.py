from datetime import date
from pathlib import Path
from typing import List, Tuple

import matplotlib

from backtest.constants import BUDGET, START_DATE
from backtest.utils import load_data_from_csv, Data, plot_graph, log_annual_returns_summary
from logger import logger

matplotlib.use("TkAgg")


def should_pass(curr_date: date, start_date: date) -> bool:
    return curr_date < start_date


def should_sell(is_holding: bool, stop_loss_price: float, low: float) -> bool:
    return is_holding and stop_loss_price > low


def should_buy(is_holding: bool, close: float, open: float) -> bool:
    return not is_holding and close > open


def backtest(
    data_list: List[Data], budget: float = BUDGET, start_date: date = START_DATE
) -> Tuple[List[date], List[float]]:
    buy_price = 0.0
    stop_loss_price = 0.0
    is_holding = False
    budget_list = []
    date_list = []

    for data in data_list:
        if should_pass(data.date, start_date):
            continue

        if should_sell(is_holding, stop_loss_price, data.low):
            sell_price = min(data.open, stop_loss_price)
            budget *= (sell_price - buy_price) / buy_price + 1
            is_holding = False
            margin_rate = ((sell_price - buy_price) / buy_price) * 100
            logger.warning(
                f"DATE: {data.date} | ACTION: Sold | SELL PRICE: ${sell_price:.2f} | "
                f"BUY PRICE: ${buy_price:.2f} | MARGIN RATE: {margin_rate:.2f}%"
            )

        elif should_buy(is_holding, data.close, data.open):
            buy_price = data.close
            is_holding = True
            logger.warning(f"DATE: {data.date} | ACTION: Bought | BUY PRICE: ${buy_price:.2f}")

        stop_loss_price = data.close
        budget_list.append(budget)
        date_list.append(data.date)
        logger.info(
            f"DATE: {data.date} | CURRENT BUDGET: ${budget:.2f} | CLOSING PRICE: ${data.close}\n"
        )

    return date_list, budget_list


if __name__ == "__main__":
    file_name = "BNKU -> X.csv"

    path = Path("backtest/data", file_name)
    data_list = load_data_from_csv(str(path))

    date_list, budget_list = backtest(data_list)
    log_annual_returns_summary(date_list, budget_list)
    plot_graph(date_list, budget_list, path.stem)
