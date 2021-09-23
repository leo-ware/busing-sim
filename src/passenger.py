from random import randint
from scipy import stats
from typing import Callable, Any

from src.event_manager import EventManager
from src.actions import PASSENGER_JOIN_QUEUE, PASSENGER_ABANDON_QUEUE, PASSENGER_EMBARK, PASSENGER_DISEMBARK


class Passenger:
    num_ps = 0

    def __init__(self, event_manager: EventManager, stop) -> None:
        """Represents a passenger in the simulation

        Args:
            event_manager: an instance of the event manager class
            stop: an instance of the stop class, the stop where the passenger is instantiated
        """
        self.event_manager = event_manager
        self.stop = stop

        # assigns a process-unique id to each Passenger
        self.id = Passenger.num_ps
        Passenger.num_ps += 1

        self.has_embarked = False
        self.initialization_time = event_manager.time
        self.stops_traveling = randint(1, 7)
        self.stops_remaining = self.stops_traveling

        self.join_queue()

    def __repr__(self) -> str:
        return f"<Passenger id={self.id}>"

    def __hash__(self) -> int:
        return self.id

    def join_queue(self) -> None:
        """Dispatches a JOIN_QUEUE action and prepares to leave if nnot picked up in 10 minutes"""

        # passenger will wait this many minutes before walking
        patience = 10

        def cb():
            if not self.has_embarked:
                self.stop.remove_passenger(self)
                self.event_manager.dispatch(self, PASSENGER_ABANDON_QUEUE, 0)
        self.event_manager.dispatch(self, PASSENGER_JOIN_QUEUE, patience, cb)

    def disembark(self, n_passengers: int, callback: Callable[[], None]) -> None:
        """Calculates duration and fires a disembark event, recording total travel time
        
        The total number of stops the Passenger traveled is recorded as data on the DISPATCHED event and
        the total time spent in transit is returned from the callback recorded as data on the FINISHED event

        Args:
            n_passengers: the number of passengers currently on the bus, including this one
            callback: called when the passenger is done disembarking (return value is ignored)
        """
        if n_passengers <= 0:
            raise ValueError("n_passengers must be positive")
        
        def cb():
            callback()
            return total_transit_time

        execution_time = max(0, stats.norm.rvs(scale=0.01*(n_passengers**0.5), loc=0.03*n_passengers))
        total_transit_time = (self.event_manager.time + execution_time) - self.initialization_time
        self.event_manager.dispatch(self, PASSENGER_DISEMBARK, execution_time, cb, self.stops_traveling)

    def embark(self, n_passengers: int, callback: Callable) -> None:
        """Calculates duration and fires a disembark event, recording total travel time

        Args:
            n_passengers: the number of passengers currently on the bus, including this one
            callback: called when the passenger is done disembarking
        """
        if n_passengers < 0:
            raise ValueError("n_passengers must be nonnegative")

        self.has_embarked = True
        execution_time = max(0, stats.norm.rvs(scale=0.01*(n_passengers**0.5), loc=0.05*n_passengers))
        self.event_manager.dispatch(self, PASSENGER_EMBARK, execution_time, callback)
