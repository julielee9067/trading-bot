import csv
import datetime
from datetime import date
from dataclasses import dataclass
from pathlib import Path
from typing import List, Any, Dict
import matplotlib.pyplot as plt

from backtest.constants import MIN_YEAR
from backtest.main import backtest
from logger import logger


@dataclass
class Data:
    date: date
    open: float
    high: float
    low: float
    close: float
    mas: float = 0.0
    mal: float = 0.0


def load_data_from_csv(file_name: str) -> List[Data]:
    data_list = []

    with open(file_name, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data = Data(
                date=datetime.datetime.strptime(row["Date"], "%Y-%m-%d").date(),
                open=round(float(row["Open"]), 2),
                high=round(float(row["High"]), 2),
                low=round(float(row["Low"]), 2),
                close=round(float(row["Close"]), 2),
            )
            data_list.append(data)

    return data_list


def plot_graph(x_values: List[Any], y_values: List[Any], file_name: str):
    plt.plot(x_values, y_values)
    plt.title(file_name)
    plt.xlabel("Time")
    plt.ylabel("Budget [$]")
    plt.savefig(Path("backtest/results", f"{file_name}.png"))
    plt.show()


def log_annual_returns_summary(
    date_list: List[date], budget_list: List[float], min_year: int = MIN_YEAR
):
    current_budget = 1.0
    current_year = min_year

    for i, (data_date, budget) in enumerate(zip(date_list, budget_list)):
        if current_year < data_date.year or i == len(date_list) - 1:
            annual_return = (
                (budget - current_budget) / current_budget * 100 if current_year != min_year else 0
            )
            logger.debug(f"{data_date}: ${round(budget, 2)}, Annual Return: {annual_return:.2f}%")
            current_year = data_date.year
            current_budget = budget


def get_moving_average(window_size: int, data_list: List[Data], index: int) -> float:
    total = 0.0
    if index - window_size < 0:
        return data_list[index].close

    for i in range(index - window_size, index):
        data = data_list[i]
        total += data.close

    return total / window_size


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
