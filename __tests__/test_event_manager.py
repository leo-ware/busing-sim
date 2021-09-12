from pytest import raises
from random import seed, shuffle

from src.event_manager import EventManager
from src.log import InMemoryLog, VoidLog


def test_validation():
    ev = EventManager(VoidLog())
    with raises(ValueError):
        ev.dispatch(None, "", -1)


def test_firing_order_loaded_together():
    seed(123)

    log = InMemoryLog()
    ev = EventManager(log)
    nums = list(range(10))
    shuffle(nums)

    calls = []

    def make_cb(i):
        def cb():
            calls.append(i)
        return cb

    for num in nums:
        ev.dispatch(None, "", num, make_cb(num))

    ev.run(100)

    assert calls == list(range(10))


def test_firing_order_loaded_dynamically():
    seed(123)
    sim = EventManager(VoidLog())

    sim.dispatch(None, "", 10)
    sim.dispatch(None, "", 5)
    sim.next()
    assert sim.time == 5

    sim.dispatch(None, "", 2)
    sim.next()
    assert sim.time == 7

    sim.run(1000)
    assert sim.time == 10
