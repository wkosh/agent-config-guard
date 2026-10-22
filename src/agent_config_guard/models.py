from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


@dataclass(frozen=True, slots=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    path: Path
    line: int = 1
    recommendation: str = ""

    def to_dict(self, root: Path) -> dict[str, object]:
        data = asdict(self)
        try:
            data["path"] = self.path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            data["path"] = self.path.as_posix()
        return data

