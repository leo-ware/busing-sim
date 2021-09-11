from typing import Union, List
from dataclasses import dataclass
from abc import abstractmethod, ABC


@dataclass(frozen=True)
class LogRecord:
    time: Union[float, int]
    obj: object
    action: str
    status: str


class Log(ABC):
    @abstractmethod
    def write(self, record: LogRecord) -> None:
        pass


class VoidLog(Log):
    def write(self, record: LogRecord) -> None:
        pass


class InMemoryLog(Log):
    def __init__(self):
        self.log: List[LogRecord] = []

    def write(self, record: LogRecord):
        self.log.append(record)
