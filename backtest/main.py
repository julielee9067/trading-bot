from datetime import datetime
from typing import List, Tuple

import matplotlib

from backtest.constants import BUDGET, START_DATE
from backtest.utils import load_data_from_csv, Data, plot_graph, log_annual_returns_summary
from logger import logger

matplotlib.use("TkAgg")


def backtest(
    data_list: List[Data], budget: float = BUDGET, start_date: datetime = START_DATE
) -> Tuple[List[datetime], List[float]]:
    buy_price = 0.0
    stop_loss_price = 0.0
    is_holding = False
    budget_list = []
    date_list = []

    for data in data_list:
        if data.date < start_date:
            continue

        if is_holding and stop_loss_price > data.low:
            sell_price = min(data.open, stop_loss_price)
            budget *= (sell_price - buy_price) / buy_price + 1
            is_holding = False
            logger.info(
                f"Sold: ${sell_price} | Bought: ${buy_price} | "
                f"Margin rate: {((sell_price - buy_price) / buy_price) * 100}%"
            )

        if not is_holding and data.close > data.open:
            buy_price = data.close
            is_holding = True
            logger.info(f"Bought at: {buy_price}")

        stop_loss_price = data.close
        budget_list.append(budget)
        date_list.append(data.date)
        logger.info(f"{data.date}: budget={budget}, close_price={data.close}\n")

    return date_list, budget_list


if __name__ == "__main__":
    file_name = "backtest/data/BNKU -> X.csv"
    data_list = load_data_from_csv(file_name)

    date_list, budget_list = backtest(data_list)
    log_annual_returns_summary(date_list, budget_list)
    plot_graph(date_list, budget_list)
