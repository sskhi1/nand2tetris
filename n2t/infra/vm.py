from __future__ import annotations

import glob
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Protocol

from n2t.core import VMTranslator as DefaultTranslator
from n2t.infra.io import File, FileFormat


@dataclass
class VmProgram:  # TODO: your work for Projects 7 and 8 starts here
    path: Path
    file_name: str
    translator: VMTranslator = field(default_factory=DefaultTranslator.create)

    @classmethod
    def load_from(cls, file_or_directory_name: str) -> VmProgram:
        return cls(Path(file_or_directory_name), file_or_directory_name)

    def translate(self) -> None:
        if os.path.isfile(self.file_name):
            asm_file = File(FileFormat.asm.convert(self.path))
            asm_file.save(self.translator.translate(self, self.file_name, False))
        elif os.path.isdir(self.file_name):
            dir_name = self.file_name.split("\\")[-1]
            path_dir = Path(self.file_name + "/" + dir_name + ".asm")
            asm_file = File(path_dir)
            in_files = glob.glob(self.file_name + "/*.vm")
            asm_file.save(self.translator.translate(in_files, dir_name, True))

    def __iter__(self) -> Iterator[str]:
        yield from File(self.path).load()


class VMTranslator(Protocol):  # pragma: no cover
    def translate(
        self, vm_code: Iterable[str], file_name: str, is_dir: bool
    ) -> Iterable[str]:
        pass
