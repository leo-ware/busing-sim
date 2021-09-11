from src.event_manager import EventManager
from src.log import VoidLog, InMemoryLog
from src.bus import Bus
from src.stop import Stop
from src.passenger import Passenger


def test_move():
    sim = EventManager(VoidLog())

    # flags will get marked True by successful test
    parked = False
    departed = False

    # dummy passenger
    class passenger:
        stops_remaining = 1

    # dummy stop
    class stop:
        @staticmethod
        def depart():
            nonlocal departed
            departed = True

        class next:
            @staticmethod
            def park(_):
                nonlocal parked
                parked = True

    # mock bus
    bus = Bus(sim, stop)
    bus.passengers.append(passenger)

    bus.move()
    sim.run(1000)

    assert passenger.stops_remaining == 0
    assert parked
    assert departed


def test_disembark():
    log = InMemoryLog()
    ev = EventManager(log)
    stop = Stop(ev)
    bus = Bus(ev, stop)

    bus.passengers = [Passenger(ev) for _ in range(5)]
    for i, p in enumerate(bus.passengers):
        p.id = i
        p.stops_remaining = i % 3

    # run initialization for passengers
    ev.run(5)
    bus.disembark()
    ev.run(3)

    id_set = set([p.id for p in bus.passengers])
    assert 0 not in id_set
    assert 3 not in id_set
    for i in [1, 2, 4]:
        assert i in id_set


def test_embark():
    ev = EventManager(VoidLog())
    stop = Stop(ev)
    stop.next = stop
    bus = Bus(ev, stop)

    stop.passengers_waiting = [Passenger(ev) for _ in range(10)]
    bus.passengers = [Passenger(ev) for _ in range(125)]

    for p in stop.passengers_waiting + bus.passengers:
        p.stops_remaining = float("inf")

    bus.embark()
    ev.run()

    assert len(bus.passengers) == 130
    assert len(stop.passengers_waiting) == 5
