from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Protocol

from n2t.core import Emulator as DefaultEmulator
from n2t.infra.io import File


@dataclass
class EmulatorProgram:
    path: Path
    file_name: str
    cycles: int
    emulator: Emulator = field(default_factory=DefaultEmulator.create)

    @classmethod
    def load_from(cls, file_name: str, cycles: int) -> EmulatorProgram:
        return cls(Path(file_name), file_name, cycles)

    def __post_init__(self) -> None:
        file_type = self.file_name.split(".")[-1]
        if file_type != "asm" and file_type != "hack":
            raise Exception("You should provide .asm or .hack file.")

    def emulate(self) -> None:
        dir_name = self.file_name.split(".")[-2]
        path_dir = Path(dir_name + ".json")
        json_file = File(path_dir)
        json_file.save(self.emulator.emulate(self, self.file_name, self.cycles))

    def __iter__(self) -> Iterator[str]:
        yield from File(self.path).load()


class Emulator(Protocol):  # pragma: no cover
    def emulate(
        self, lines: Iterable[str], file_name: str, cycles: int
    ) -> Iterable[str]:
        pass
