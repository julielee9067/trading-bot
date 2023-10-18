from datetime import date
from enum import Enum

MIN_YEAR = 2000
BUDGET = 5000
START_DATE = date(2020, 1, 1)
END_DATE = date(2023, 10, 1)


class LongWindowSize(Enum):
    FNGU = 16
    NRGU = 30


class ShortWindowSize(Enum):
    FNGU = 3
    NRGU = 3
