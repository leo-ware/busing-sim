from src.stop import Stop
from src.event_manager import EventManager
from src.log import InMemoryLog


def test_passenger_arrival():
    log = InMemoryLog()
    sim = EventManager(log)
    stop = Stop(sim)
    stop.passenger_arrives()
    sim.run(10)

    # exact number of passengers created is undefined, but it will be at least 3 if stuff works
    assert len(stop.passengers_waiting) > 3


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
