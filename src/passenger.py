from random import randint
from scipy import stats
from typing import Callable

from src.event_manager import EventManager


class Passenger:
    num_ps = 0

    def __init__(self, event_manager: EventManager) -> None:
        event_manager.dispatch(self, "JOIN_QUEUE", 0)
        self.event_manager = event_manager

        # assigns a process-unique id to each Passenger
        self.id = Passenger.num_ps
        Passenger.num_ps += 1

        self.stops_remaining = randint(1, 7)

    def __repr__(self):
        return f"<Passenger id={self.id}>"

    def __hash__(self):
        return self.id

    def disembark(self, n_passengers: int, callback: Callable):
        if n_passengers < 0:
            raise ValueError("n_passengers must be nonnegative")

        execution_time = max(0, stats.norm.rvs(scale=0.01*n_passengers**0.5, loc=0.03*n_passengers))
        self.event_manager.dispatch(self, "DISEMBARK", execution_time, callback)

    def embark(self, n_passengers: int, callback: Callable):
        if n_passengers < 0:
            raise ValueError("n_passengers must be nonnegative")

        execution_time = max(0, stats.norm.rvs(scale=0.01*n_passengers**0.5, loc=0.05*n_passengers))
        self.event_manager.dispatch(self, "EMBARK", execution_time, callback)
