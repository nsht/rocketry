
from datetime import datetime

from pypipe.builtin.time.interval import (
    TimeOfDay, DaysOfWeek
)

import pytest


@pytest.mark.parametrize(
    "dt,start,end",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 10, 00),
            "10:00", "12:00",
            id="Left of interval"),
        pytest.param(
            datetime(2020, 1, 1, 12, 00),
            "10:00", "12:00",
            id="Right of interval"),
        pytest.param(
            datetime(2020, 1, 1, 11, 00),
            "10:00", "12:00",
            id="Middle of interval"),

        # Overnight
        pytest.param(
            datetime(2020, 1, 1, 22, 00),
            "22:00", "02:00",
            id="Left of overnight interval"),
        pytest.param(
            datetime(2020, 1, 1, 2, 00),
            "22:00", "02:00",
            id="Right of overnight interval"),
        pytest.param(
            datetime(2020, 1, 1, 23, 59, 59, 999999),
            "22:00", "02:00",
            id="Middle left of overnight interval"),
        pytest.param(
            datetime(2020, 1, 1, 00, 00),
            "22:00", "02:00",
            id="Middle right of overnight interval"),

        # Full Cycle
        pytest.param(
            datetime(2020, 1, 1, 10, 00),
            None, None,
            id="Full interval"),
        pytest.param(
            datetime(2020, 1, 1, 10, 00),
            "10:00", "10:00",
            id="Joint of full interval"),
        pytest.param(
            datetime(2020, 1, 1, 12, 00),
            "10:00", "10:00",
            id="Right of full interval"),
        pytest.param(
            datetime(2020, 1, 1, 8, 00),
            "10:00", "10:00",
            id="Left of full interval"),
    ],
)
def test_in_timeofday(start, end, dt):
    time = TimeOfDay(start, end)
    assert dt in time


@pytest.mark.parametrize(
    "dt,start,end",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 9, 59, 59, 999999),
            "10:00", "12:00",
            id="Left from interval"),
        pytest.param(
            datetime(2020, 1, 1, 12, 00, 00, 1),
            "10:00", "12:00",
            id="Right from interval"),

        # Overnight
        pytest.param(
            datetime(2020, 1, 1, 21, 59, 59, 999999),
            "22:00", "02:00",
            id="Left from overnight interval"),
        pytest.param(
            datetime(2020, 1, 1, 2, 00, 00, 1),
            "22:00", "02:00",
            id="Right from overnight interval"),
    ],
)
def test_not_in_timeofday(start, end, dt):
    time = TimeOfDay(start, end)
    assert dt not in time


@pytest.mark.parametrize("dt", [datetime(2020, 6, 1, 0, 0), datetime(2020, 6, 5, 23, 59)])
def test_daysofweek_true(dt):
    time = DaysOfWeek("Mon", "Fri")
    assert dt in time

@pytest.mark.parametrize("dt", [datetime(2020, 6, 2, 0, 0), datetime(2020, 6, 4, 23, 59)])
def test_daysofweek_false(dt):
    time = DaysOfWeek("Mon", "Fri")
    assert dt not in time

