from dataclasses import dataclass
from queue import PriorityQueue
from typing import Callable

from src.log import Log, LogRecord


@dataclass(frozen=True)
class Event:
    """Class used internally in Sim to store upcoming events

    Args:
        time: the time (in sim mins) when the event finishes
        callback: function to execute when the event is finished
    """
    time: float
    callback: Callable[[float], None]

    def __lt__(self, other):
        if not isinstance(other, Event):
            raise ValueError(f"cannot compare Event to {other.__class__}")
        return self.time < other.time


class EventManager:

    def __init__(self, log: Log):
        """Class that governs the game clock and executes events in order

        Args:
            log: a log object
        """
        self._n_dispatches = 1000
        self.log = log
        self.queue = PriorityQueue()
        self._time = 0

    @property
    def time(self):
        """getter for self._time, protects value from accidental tampering"""
        return self._time

    def dispatch(self, obj: object, action: str, duration: float, callback: Callable = (lambda: None), data=None) -> None:
        """Adds an event to the queue

        Args:
            obj: the object initiating this action
            action: the type of action being performed
            duration: the length (in sim minutes) of the event
            callback: function to execute when the event is finished
        """
        if duration < 0:
            raise ValueError("duration must be nonnegative")

        event_id = self._n_dispatches
        self._n_dispatches += 1

        def cb(time: float) -> None:
            callback()
            self.log.write(LogRecord(event_id, time, obj, action, "FINISHED", data))

        self.log.write(LogRecord(event_id, self.time, obj, action, "DISPATCHED", data))

        self.queue.put(Event(
            time=self.time + duration,
            callback=cb
        ))

    def next(self) -> None:
        """Move the sim clock forward until the next event finishes and execute callback"""
        task = self.queue.get()
        self._time = task.time
        task.callback(self.time)

    def run(self, max_events=float("inf"), stop_time=float("inf")) -> None:
        """Run the simulation

        Args:
            max_events: only run this many events at maximum
            stop_time: stop after this many game minutes have elapsed
        """
        i = 0
        while not self.queue.empty() and self.time < stop_time:
            self.next()
            i += 1
            if i >= max_events:
                break
