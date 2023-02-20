from abc import ABC
from dataclasses import dataclass


class SystemEvent(ABC):
    """Event in the system"""


@dataclass
class ErrorRaised(SystemEvent):
    msg: str
