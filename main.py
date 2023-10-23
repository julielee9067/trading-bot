import time
from datetime import datetime

import pytz  # type: ignore
import schedule


def main():
    est_timezone = pytz.timezone("US/Eastern")
    print(datetime.now(est_timezone).replace(hour=9, minute=0, second=0, microsecond=0))

    # schedule.every().day.at(job_time.strftime("%H:%M")).do(job)


if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
