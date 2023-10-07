from datetime import date
from pathlib import Path
from typing import List, Tuple, Dict

import matplotlib

from backtest.constants import BUDGET, START_DATE, END_DATE, ShortWindowSize, LongWindowSize
from backtest.utils import (
    load_data_from_csv,
    Data,
    plot_graph,
    log_annual_returns_summary,
    get_moving_average,
)
from logger import logger

matplotlib.use("TkAgg")


def should_pass(curr_date: date, start_date: date) -> bool:
    return curr_date < start_date


def should_sell(is_holding: bool, stop_loss_price: float, low: float) -> bool:
    return is_holding and stop_loss_price > low


def should_buy(is_holding: bool, data: Data) -> bool:
    return not is_holding and data.close > data.open and data.mas >= data.mal


def backtest(
    data_list: List[Data],
    short_ws: int,
    long_ws: int,
    budget: float = BUDGET,
    start_date: date = START_DATE,
    end_date: date = END_DATE,
) -> Tuple[List[date], List[float]]:
    buy_price = 0.0
    stop_loss_price = 0.0
    is_holding = False
    budget_list = []
    date_list = []

    for index, data in enumerate(data_list):
        data.mas = get_moving_average(short_ws, data_list, index)
        data.mal = get_moving_average(long_ws, data_list, index)

        if data.date > end_date:
            break

        if should_pass(data.date, start_date):
            continue

        if should_sell(is_holding, stop_loss_price, data.low):
            sell_price = min(data.open, stop_loss_price) * 0.995
            budget *= (sell_price - buy_price) / buy_price + 1
            is_holding = False
            margin_rate = ((sell_price - buy_price) / buy_price) * 100
            logger.warning(
                f"DATE: {data.date} | ACTION: Sold | SELL PRICE: ${sell_price:.2f} | "
                f"BUY PRICE: ${buy_price:.2f} | MARGIN RATE: {margin_rate:.2f}%"
            )

        if should_buy(is_holding, data):
            buy_price = data.close
            is_holding = True
            logger.warning(
                f"DATE: {data.date} | ACTION: Bought | OPENING PRICE: ${data.open} | "
                f"BUY PRICE: ${buy_price:.2f}"
            )

        stop_loss_price = data.close * 0.99
        budget_list.append(budget)
        date_list.append(data.date)
        logger.info(
            f"DATE: {data.date} | BUDGET: ${budget:.2f} | "
            f"OPENING: ${data.open} | CLOSING: ${data.close} | MAL: {data.mal:.2f} | "
            f"MAS: {data.mas:.2f}\n"
        )

    return date_list, budget_list


def get_res_by_file_name(file_name: str, short, long) -> Tuple[List[date], List[float]]:
    path = Path("backtest/data", file_name)
    data_list = load_data_from_csv(str(path))
    date_list, budget_list = backtest(data_list, short, long)

    return date_list, budget_list


def get_optimal_window_sizes(data_list: List[Data]) -> List[Dict]:
    ma_budget_list = []
    for i in range(1, 60):
        for j in range(1, i):
            date_list, budget_list = backtest(data_list, i, j)
            final_budget = budget_list[-1]
            ma_budget_list.append(
                {"short_window_size": j, "long_window_size": i, "budget": final_budget}
            )

    ma_budget_list.sort(key=lambda x: x["budget"])
    return ma_budget_list


if __name__ == "__main__":
    FNGU = "FNGU.csv"
    NGRU = "NRGU.csv"

    date_list, FNGU_budget_list = get_res_by_file_name(
        FNGU, ShortWindowSize.FNGU.value, LongWindowSize.FNGU.value
    )
    _, NGRU_budget_list = get_res_by_file_name(
        NGRU, ShortWindowSize.NRGU.value, LongWindowSize.NRGU.value
    )

    res_budget_list = [
        (first + second) for first, second in zip(FNGU_budget_list, NGRU_budget_list)
    ]
    log_annual_returns_summary(date_list, res_budget_list)
    plot_graph(date_list, res_budget_list, Path("SUM").stem)

    # get_optimal_window_sizes(data_list)
