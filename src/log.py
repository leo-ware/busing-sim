from typing import Callable, Union, List, Any
from dataclasses import dataclass
from abc import abstractmethod, ABC
import datetime
import os


@dataclass(frozen=True)
class LogRecord:
    id: int
    time: Union[float, int]
    obj: object
    action: str
    status: str
    data: Any = None


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
            f.write("event_id,time,object_type,object_id,action,status,data\n")

    def write_to_file(self):
        with open(self.f_name, "a") as f:
            f.write("\n".join([
                f"{r.id},{r.time},{r.obj.__class__.__name__},{r.obj.id},{r.action},{r.status},{r.data}"
                for r in self.log
            ]) + "\n")
        self.log = []

    def write(self, record: LogRecord) -> None:
        self.log.append(record)
        if len(self.log) >= self.buffer_size:
            self.write_to_file()

    def close(self) -> None:
        self.write_to_file()


class LogFilter(Log):
    def __init__(self, base_log: Log, keep: Callable[[LogRecord], bool]):
        self.keep = keep
        self.base_log = base_log
    
    def write(self, record: LogRecord) -> None:
        if self.keep(record):
            self.base_log.write(record)
    
    def close(self) -> None:
        return self.base_log.close()
