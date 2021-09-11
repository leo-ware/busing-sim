from dataclasses import dataclass
from queue import PriorityQueue
from typing import Callable
from inspect import signature

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
        self.log = log
        self.queue = PriorityQueue()
        self.time = 0

    def dispatch(self, obj: object, action: str, duration: float, callback: Callable = (lambda _: None)) -> None:
        """Adds an event to the queue

        Args:
            obj: the object initiating this action
            action: the type of action being performed
            duration: the length (in sim minutes) of the event
            callback: function to execute when the event is finished
        """
        if duration < 0:
            raise ValueError("duration must be nonnegative")

        def cb(time: float) -> None:
            if len(signature(callback).parameters):
                callback(time)
            else:
                callback()

            self.log.write(LogRecord(time, obj, action, "FINISHED"))

        self.log.write(LogRecord(self.time, obj, action, "DISPATCHED"))

        self.queue.put(Event(
            time=self.time + duration,
            callback=cb
        ))

    def next(self) -> None:
        """Move the sim clock forward until the next event finishes and execute callback"""
        task = self.queue.get()
        self.time = task.time
        task.callback(self.time)

    def run(self, max_events: int = 10000) -> None:
        """Run the simulation

        Args:
            max_events: only run this many events at maximum
        """
        i = 0
        while not self.queue.empty():
            self.next()
            i += 1
            if i >= max_events:
                break
