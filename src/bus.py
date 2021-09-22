from scipy import stats
from typing import List

from src.event_manager import EventManager
from src.passenger import Passenger


class Bus:

    # simulation parameters
    TRAVEL_TIME_AVERAGE = 3
    TRAVEL_TIME_STD = 0.5
    BUS_MAX_CAPACITY = 130

    # how many buses are in operation
    _bus_num = 0

    def __init__(self, event_manager: EventManager, stop):
        self.event_manager = event_manager
        self.passengers: List[Passenger] = []
        self.stop = stop

        self.thing = None

        # assigns a process-unique id to each Bus
        self.id = Bus._bus_num
        Bus._bus_num += 1

    def __repr__(self):
        return f"<Bus id={self.id}>"

    def __hash__(self):
        return self.id

    def move(self):
        """Go to the next stop, decrement passenger step counters, and request to park"""

        # notify the stop that we are leaving
        self.stop.depart()

        execution_time = stats.norm.rvs(
                loc=Bus.TRAVEL_TIME_AVERAGE,
                scale=Bus.TRAVEL_TIME_STD
            )

        def cb():
            self.stop = self.stop.next
            for p in self.passengers:
                p.stops_remaining -= 1

            # hands control to stop, control will be restored via call to disembark when the stop loads the bus
            self.stop.park(self)

        self.event_manager.dispatch(self, "MOVE", execution_time, cb)

    def disembark(self):
        """Exit all passengers who belong at the station, then request to embark"""
        n_passengers = len(self.passengers)
        disembarking_passengers = tuple(p for p in self.passengers if p.stops_remaining == 0)
        i = 0

        def disembark_next():
            nonlocal i, disembarking_passengers, n_passengers

            if i < len(disembarking_passengers):

                # note passengers are unloaded in same order as they loaded: FIFO
                disembarking_passenger = disembarking_passengers[i]

                i += 1

                # hands control to the passenger
                disembarking_passenger.disembark(
                    n_passengers - i + 1,
                    disembark_next          # control returned via callback
                )

            else:
                transiting_set = set(disembarking_passengers)
                self.passengers = [p for p in self.passengers if p not in transiting_set]
                self.embark()

        self.event_manager.dispatch(self, "BUS_DISEMBARK", 0, disembark_next)

    def embark(self):
        """Board passengers, then request to move"""

        def embark_next():
            if len(self.passengers) < Bus.BUS_MAX_CAPACITY and self.stop.passengers_waiting:
                embarking = self.stop.passengers_waiting.pop()

                def cb():
                    self.passengers.append(embarking)
                    embark_next()

                embarking.embark(len(self.passengers), cb)
            else:
                self.move()

        self.event_manager.dispatch(self, "BUS_EMBARK", 0, embark_next)
