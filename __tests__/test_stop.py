from src.stop import Stop
from src.event_manager import EventManager
from src.log import InMemoryLog, VoidLog
from src.actions import PASSENGER_JOIN_QUEUE


def test_passenger_arrival():
    log = InMemoryLog()
    sim = EventManager(log)
    stop = Stop(sim)
    stop.passenger_arrives()
    sim.run(10)

    # exact number of passengers created is undefined, but it will be at least 3 if stuff works
    assert len([record for record in log.log if record.action == PASSENGER_JOIN_QUEUE]) > 3


# global flag marked true by successful tests
disembarked = False


def test_load():
    sim = EventManager(InMemoryLog())
    stop = Stop(sim)

    global disembarked
    disembarked = False

    # dummy bus
    class bus:
        @staticmethod
        def disembark():
            global disembarked
            disembarked = True

    stop.park(bus)
    assert disembarked


def test_expected_arrival_interval():
    stop = Stop(EventManager(VoidLog()))
    assert stop.expected_arrival_interval(7*60) < stop.expected_arrival_interval(12*60)
    assert stop.expected_arrival_interval(1 * 60) == stop.expected_arrival_interval(25 * 60)
    assert stop.expected_arrival_interval(7 * 60) == stop.expected_arrival_interval(19 * 60)
    assert stop.expected_arrival_interval(7.1 * 60) == stop.expected_arrival_interval(19 * 60)
