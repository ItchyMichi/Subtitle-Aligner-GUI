from dataclasses import dataclass
from typing import Optional

@dataclass
class SubtitleEvent:
    start: Optional[float]
    end: Optional[float]
    text: str
