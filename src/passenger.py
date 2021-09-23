from random import randint
from scipy import stats
from typing import Callable

from src.event_manager import EventManager


class Passenger:
    num_ps = 0

    def __init__(self, event_manager: EventManager, stop) -> None:
        self.event_manager = event_manager
        self.stop = stop

        # assigns a process-unique id to each Passenger
        self.id = Passenger.num_ps
        Passenger.num_ps += 1

        self.has_embarked = False
        self.initialization_time = event_manager.time
        self.stops_remaining = randint(1, 7)

        self.join_queue()

    def __repr__(self):
        return f"<Passenger id={self.id}>"

    def __hash__(self):
        return self.id

    def join_queue(self):
        # passenger will wait this many minutes before walking
        patience = 10

        def cb():
            if not self.has_embarked:
                self.stop.remove_passenger(self)
                self.event_manager.dispatch(self, "ABANDON_QUEUE", 0)
        self.event_manager.dispatch(self, "JOIN_QUEUE", patience, cb)

    def disembark(self, n_passengers: int, callback: Callable):
        if n_passengers <= 0:
            raise ValueError("n_passengers must be positive")

        execution_time = max(0, stats.norm.rvs(scale=0.01*(n_passengers**0.5), loc=0.03*n_passengers))
        total_transit_time = (self.event_manager.time + execution_time) - self.initialization_time
        self.event_manager.dispatch(self, "PASSENGER_DISEMBARK", execution_time, callback, total_transit_time)

    def embark(self, n_passengers: int, callback: Callable):
        if n_passengers < 0:
            raise ValueError("n_passengers must be nonnegative")

        self.has_embarked = True
        execution_time = max(0, stats.norm.rvs(scale=0.01*(n_passengers**0.5), loc=0.05*n_passengers))
        self.event_manager.dispatch(self, "PASSENGER_EMBARK", execution_time, callback)
