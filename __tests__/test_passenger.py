from pytest import raises

from src.log import InMemoryLog
from src.event_manager import EventManager
from src.passenger import Passenger
from src.stop import Stop


def test_fires_callback():

    def cb():
        nonlocal flag
        flag = True

    ev = EventManager(InMemoryLog())
    p = Passenger(ev, Stop(ev))

    with raises(ValueError):
        p.disembark(-1, cb)

    flag = False
    p.disembark(1, cb)
    ev.run(100)
    assert flag

    flag = False
    p.disembark(10, cb)
    ev.run(100)
    assert flag

    with raises(ValueError):
        p.embark(-1, cb)

    flag = False
    p.embark(0, cb)
    ev.run(100)
    assert flag

    flag = False
    p.embark(10, cb)
    ev.run(100)
    assert flag


def test_dispatches_events():
    log = InMemoryLog()
    ev = EventManager(log)
    p = Passenger(ev, Stop(ev))
    p.disembark(1, lambda: None)
    p.embark(1000, lambda: None)
    assert [record.action for record in log.log] == ["JOIN_QUEUE", "PASSENGER_DISEMBARK", "PASSENGER_EMBARK"]
