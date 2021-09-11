from typing import Union, List
from dataclasses import dataclass
from abc import abstractmethod, ABC
import datetime
import os


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

    def close(self) -> None:
        pass


class VoidLog(Log):
    def write(self, record: LogRecord) -> None:
        pass


class InMemoryLog(Log):
    def __init__(self):
        self.log: List[LogRecord] = []

    def write(self, record: LogRecord):
        self.log.append(record)


class CSVLog(Log):
    def __init__(self, path="", msg="", buffer_size=1000):
        self.buffer_size = buffer_size
        self.log = []

        self.f_name = f"log_{msg}_{str(datetime.datetime.now())}.csv"
        if path:
            self.f_name = os.path.join(path, self.f_name)

        with open(self.f_name, "a") as f:
            f.write("time,type,id,action,status\n")

    def write_to_file(self):
        with open(self.f_name, "a") as f:
            f.write("\n".join([
                f"{r.time},{r.obj.__class__.__name__},{r.obj.id},{r.action},{r.status}"
                for r in self.log
            ]))
        self.log = []

    def write(self, record: LogRecord) -> None:
        self.log.append(record)
        if len(self.log) >= self.buffer_size:
            self.write_to_file()

    def close(self) -> None:
        self.write_to_file()
