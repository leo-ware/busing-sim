from typing import Optional

from src.log import InMemoryLog, Log
from src.event_manager import EventManager
from src.stop import Stop
from src.bus import Bus


class Sim:

    n_stops = 15

    def __init__(self, n_buses: int, log: Optional[Log] = None):

        if n_buses <= 0:
            raise ValueError("n_buses must be strictly positive")
        self.n_buses = n_buses

        self.log = log if log else InMemoryLog()
        self.event_manager = EventManager(self.log)
        self.route = self.create_route()
        self.buses = self.create_buses()

        self.start()

    def create_route(self):
        """Creates all the stops and arranges them as a circular linked list"""
        stops = [Stop(self.event_manager) for _ in range(Sim.n_stops)]
        for i in range(Sim.n_stops):
            stops[i-1].next = stops[i]
        return stops

    def create_buses(self):
        """Creates the buses and assigns them to stops"""
        return [Bus(self.event_manager, self.route[i % Sim.n_stops]) for i in range(self.n_buses)]

    def start(self):
        """Tells all the buses to start moving"""
        for bus in self.buses:
            bus.move()
        for stop in self.route:
            stop.start()

    def run(self, n_steps):
        self.event_manager.run(n_steps)
        self.log.close()
