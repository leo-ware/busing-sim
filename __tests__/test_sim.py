import pytest

from src.sim import Sim
from src.actions import BUS_MOVE


def test_init():
    sim = Sim(15)

    # all the buses have been assigned unique stops
    assert len(set([bus.stop for bus in sim.buses])) == 15

    # all the buses have been told to move
    assert len(set([record.obj.id for record in sim.log.log if record.action == BUS_MOVE])) == 15

    # route setup
    assert set(sim.route) == set([stop.next for stop in sim.route])
    assert sim.route[0].next == sim.route[1]

    # it runs
    sim.run(10)


def test_init_bad_inputs():
    with pytest.raises(ValueError):
        Sim(0)
    with pytest.raises(ValueError):
        Sim(-100)


def test_finite_duration():
    sim = Sim(1)
    sim.run(10)
