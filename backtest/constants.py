from datetime import date
from enum import Enum

MIN_YEAR = 2000
BUDGET = 5000
START_DATE = date(2022, 4, 1)
END_DATE = date(2023, 10, 1)


class LongWindowSize(Enum):
    FNGU = 21
    NRGU = 1


class ShortWindowSize(Enum):
    FNGU = 1
    NRGU = 1
