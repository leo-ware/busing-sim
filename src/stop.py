from scipy import stats
from collections import deque
from math import cos, pi, floor

from src.event_manager import EventManager
from src.passenger import Passenger
from src.actions import STOP_PASSENGER_JOIN, STOP_REPORT_QUEUE_LENGTH

QUEUE_LEN_REPORT_FREQUENCY = 10


class Stop:
    _stop_num = 0

    def __init__(self, event_manager: EventManager, next_stop=None) -> None:

        # parameters
        self.event_manager = event_manager
        self.next = next_stop

        # assigns a process-unique id to each Stop
        self.id = Stop._stop_num
        Stop._stop_num += 1

        # state
        self.bus_loading = None
        self.bus_queue = deque()
        self.passengers_waiting = deque()

    def __repr__(self):
        return f"<Stop id={self.id}>"

    def __hash__(self):
        return self.id

    def load(self):
        """Circumstances permitting, load the next bus in line"""
        if not self.bus_loading and self.bus_queue:
            self.bus_loading = self.bus_queue.pop()

        if self.bus_loading:
            self.bus_loading.disembark()

    def park(self, bus) -> None:
        """Called by buses as they arrive. The new bus is added to bus_queue, and loaded if the stop is free.

        Args:
            bus: the bus that has just arrived
        """
        self.bus_queue.appendleft(bus)
        self.load()

    def depart(self) -> None:
        """Called by buses as they depart. Stop begins loading the next bus.

        If there is another bus waiting to load, we load it now. Otherwise, we do nothing.
        """
        self.bus_loading = None
        self.load()

    def expected_arrival_interval(self, time):
        """Calculates the expected time between passenger arrivals, as a function of sim time

        We get the time of day from the sim time by dividing by sixty (minutes -> hours), removing the decimal (hours +
        minutes -> hours) and then moding by 24 (sim hours -> time of day). This assumes the simulation starts at
        midnight. The interval between successive arrivals is determined by the time of day according to the formula:

        $$
        {1 \over 1.2 + \cos(\pi (t - 7) / 6)}
        $$

        This is a distorted cosine wave that simulates a "rush hour" every day in the hours around 7am and 7pm, when the
        time between successive arrivals gets very low.
        """
        time_in_hours = floor(time / 60) % 24
        return 1/(1.2 + cos(pi * (time_in_hours - 7) / 6))

    def passenger_arrives(self) -> None:
        """Method to manager passenger arrivals

        Creates a request to the sim which, after time delay
            - creates a passenger
            - adds it to this stop
            - calls this method, causing the process to repeat
        """

        # execution time varies by time of day

        execution_time = stats.expon.rvs(scale=self.expected_arrival_interval(self.event_manager.time))

        def cb():
            passenger = Passenger(self.event_manager, self)
            self.passengers_waiting.appendleft(passenger)
            self.passenger_arrives()

        self.event_manager.dispatch(self, STOP_PASSENGER_JOIN, execution_time, cb)

    def remove_passenger(self, passenger: Passenger):
        # error handling here to make mocking easier in tests
        try:
            # O(n) to remove, but queue length should stay small
            self.passengers_waiting.remove(passenger)
        except ValueError:
            pass
    
    def report_queue_length(self):
        self.event_manager.dispatch(self, STOP_REPORT_QUEUE_LENGTH, QUEUE_LEN_REPORT_FREQUENCY, self.report_queue_length, len(self.passengers_waiting))
    
    def start(self):
        self.passenger_arrives()
        self.report_queue_length()
