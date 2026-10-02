""" PyTests für Candle                                Version 1.0 / {{HASH}} """
import dataclasses
import random
import sys
from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from candle import Candle
from sizeerror import SizeError


def test_init_default():
    candle = Candle()
    assert candle.length == 5.0
    assert candle._start_burn is None


def test_init_valid(random_length):
    candle = Candle(random_length)
    assert candle.length == random_length
    assert candle._length == random_length


def test_init_too_low(random_length):
    with pytest.raises(SizeError):
        Candle(random_length - 100)


def test_init_too_high(random_length):
    with pytest.raises(SizeError):
        Candle(random_length + 1000)
    assert True


def test_set_length(candle, random_length):
    candle.length = random_length
    assert candle._length == random_length


def test_set_length_illegal(candle, random_length):
    with pytest.raises(SizeError):
        candle.length = random_length * -1
        assert True
    with pytest.raises(SizeError):
        candle.length = random_length + 1000
        assert True


def test_light(candle):
    if sys.version_info >= (3, 8) and \
            hasattr(candle, 'light') and callable(candle.light):
        candle.light()
        assert candle._start_burn is not None
    else:
        pytest.fail('light method not implemented')


def test_light_twice(candle):
    if sys.version_info >= (3, 8) and \
            hasattr(candle, 'light') and callable(candle.light):
        with freeze_time('2024-10-03 16:00'):
            candle.light()
            assert candle._start_burn is not None
            start = candle._start_burn
            candle.light()
            assert candle._start_burn == start
    else:
        pytest.fail('light method not implemented')


def test_start_burn(candle):
    if sys.version_info < (3, 10) or hasattr(candle, 'start_burn'):
        timestamp = datetime(1970, 10, 19, 15, 3, 0, 0)
        candle.start_burn = timestamp
        assert candle.start_burn == timestamp
    else:
        pytest.skip('Skipped compatibility test')


def test_extinguish_without_burn(candle, random_length):
    if hasattr(candle, 'extinguish') and callable(candle.extinguish):
        candle.extinguish()
        assert candle._start_burn is None
        assert candle.length == random_length
    else:
        pytest.fail('extinguish method not implemented')


def test_time_left(candle, random_length):
    left = int(random_length / 2.5)
    assert candle.time_left == left


def test_extinguish(candle):
    if sys.version_info >= (3, 10) and \
            hasattr(candle, 'light') and callable(candle.light) and \
            hasattr(candle, 'extinguish') and callable(candle.extinguish):
        starting_length = candle.length
        ending_length = starting_length - 12.5
        with freeze_time('2024-10-03 16:00'):
            candle.light()
        with freeze_time('2024-10-03 16:05'):
            candle.extinguish()
            assert candle._start_burn is None
            assert pytest.approx(candle.length, None, 0.1) == ending_length
    else:
        pytest.fail('light and/or extinguish method not implemented')


def test_burn_time(candle, random_time):
    if sys.version_info < (3, 8) or hasattr(candle, 'burn_time'):
        starttime = datetime.now() - timedelta(minutes=random_time)
        candle.start_burn = starttime
        assert candle.burn_time() == 5
    else:
        pytest.skip('Skipped compatibility test')


@pytest.fixture
def candle(random_length):
    return Candle(random_length)


@pytest.fixture
def random_length(capsys):
    length_amount = round(random.uniform(32, 67), 1)
    with capsys.disabled():
        print(f' / executing test with length={length_amount}')
    return length_amount


@pytest.fixture
def random_time():
    return random.randint(5, 15)


@pytest.fixture(autouse=True)
def skip_if_wrong_class(capsys):
    if dataclasses.is_dataclass(Candle):
        pytest.skip('Candle must not be a dataclass')
        with capsys.disabled():
            print(' / skipped test because Candle must not a dataclass')
    else:
        yield
