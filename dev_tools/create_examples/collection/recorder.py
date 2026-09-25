"""repo-map-desc: User entrypoint `example` and it's inner class `Example`

The equality operator is where the magic happens
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Self

import attrs

from .record import ExampleRecord


@attrs.define
class Recorder:
    path: Path = Path("./.papertrail_cache/examples.json")
    records: list[ExampleRecord] = attrs.field(factory=list)
    files: dict[Path, str] = attrs.field(factory=dict)

    def __attrs_post_init__(self) -> None:
        self.path = Path(self.path)

    def record_example(self, example: ExampleRecord) -> Self:
        self.records.append(example)
        return self

    def prepare_files(self) -> Self:
        self.files[self.path] = json.dumps([r.to_dict() for r in self.records], indent=2)
        self.files[self.path.parent / ".gitignore"] = "# automatically created by papertrail\n*"
        return self

    def write_examples(self) -> Self:
        for path, data in self.files.items():
            path.write_text(data)
        return self


_RECORDER = Recorder()
