import csv
import datetime
from dataclasses import dataclass
from typing import List, Any
import matplotlib.pyplot as plt

from backtest.constants import MIN_YEAR
from logger import logger


@dataclass
class Data:
    date: datetime.datetime
    open: float
    high: float
    low: float
    close: float


def load_data_from_csv(file_name: str) -> List[Data]:
    data_list = []

    with open(file_name, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data = Data(
                date=datetime.datetime.strptime(row["Date"], "%Y-%m-%d"),
                open=round(float(row["Open"]), 2),
                high=round(float(row["High"]), 2),
                low=round(float(row["Low"]), 2),
                close=round(float(row["Close"]), 2),
            )
            data_list.append(data)

    return data_list


def plot_graph(x_values: List[Any], y_values: List[Any]):
    plt.plot(x_values, y_values)
    plt.show()


def log_annual_returns_summary(
    date_list: List[datetime.datetime], budget_list: List[float], min_year: int = MIN_YEAR
):
    current_budget = 1.0
    current_year = min_year

    for i, (date, budget) in enumerate(zip(date_list, budget_list)):
        if current_year < date.year or i == len(date_list) - 1:
            annual_return = (
                (budget - current_budget) / current_budget * 100 if current_year != min_year else 0
            )
            logger.debug(f"{date.date()}: ${round(budget, 2)}, Annual Return: {annual_return:.2f}%")
            current_year = date.year
            current_budget = budget
