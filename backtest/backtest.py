import csv
import datetime
from dataclasses import dataclass
from typing import List

import matplotlib

matplotlib.use('TkAgg')
from matplotlib import pyplot as plt


@dataclass
class Data:
    date: datetime.datetime
    open: float
    high: float
    low: float
    close: float


def read_csv() -> List[Data]:
    with open("data/NRGU.csv", "r") as f:
        reader = csv.DictReader(f)
        res = []
        for r in reader:
            res.append(
                Data(
                    date=datetime.datetime.strptime(r["Date"], "%Y-%m-%d"),
                    open=round(float(r["Open"]), 2),
                    high=round(float(r["High"]), 2),
                    low=round(float(r["Low"]), 2),
                    close=round(float(r["Close"]), 2)
                )
            )
    return res


def create_graph(date_list: List[datetime.datetime], budget_list: List[float]):
    last_print = 2018
    last_budget = 1
    for i, (date, budget) in enumerate(zip(date_list, budget_list)):
        if last_print < date.year or i == len(date_list) - 1:
            print((budget - last_budget)/last_budget * 100)
            print(date, budget)
            print()
            last_print = date.year
            last_budget = budget

    plt.plot(date_list, budget_list)
    plt.show()


def backtest():
    data_list = read_csv()
    start_date = datetime.datetime(2019, 5, 1)
    buy_price = 0
    stop_loss_price = 0
    budget = 10000
    is_holding = False
    budget_list = []
    date_list = []

    for data in data_list:
        if data.date < start_date:
            continue

        if is_holding and stop_loss_price > data.low:
            sell_price = data.open if data.open < stop_loss_price else stop_loss_price
            budget *= ((sell_price - buy_price)/buy_price + 1)
            is_holding = False
            print(f"Sold at: {sell_price} & bought at: {buy_price} & {((sell_price - buy_price)/buy_price) * 100}%")

        if not is_holding and data.close > data.open:
            buy_price = data.close
            is_holding = True
            print(f"Bought at: {buy_price}")

        stop_loss_price = data.close
        budget_list.append(budget)
        date_list.append(data.date)
        print(f"{data.date}: budget={budget}, close_price={data.close}")
        print()

    create_graph(date_list, budget_list)


if __name__ == "__main__":
    backtest()
