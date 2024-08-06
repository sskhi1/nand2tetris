from __future__ import annotations

import glob
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Protocol

from n2t.core import JackCompiler as DefaultCompiler
from n2t.infra.io import File


@dataclass
class JackProgram:  # TODO: your work for Projects 10 and 11 starts here
    path: Path
    file_name: str
    compiler: JackCompiler = field(default_factory=DefaultCompiler.create)

    @classmethod
    def load_from(cls, file_or_directory_name: str) -> JackProgram:
        return cls(Path(file_or_directory_name), file_or_directory_name)

    def compile(self) -> None:
        if os.path.isfile(self.file_name):
            dir_name = self.file_name.split(".")[-2]
            path_dir = Path(dir_name + ".vm")
            vm_file = File(path_dir)
            p = Path(self.file_name)
            program = JackProgram(p, self.file_name)
            vm_file.save(self.compiler.compile(program))
        elif os.path.isdir(self.file_name):
            in_files = glob.glob(self.file_name + "/*.jack")
            for file in in_files:
                print(file)
                dir_name = file.split(".")[-2]
                path_dir = Path(dir_name + ".vm")
                vm_file = File(path_dir)
                p = Path(file)
                program = JackProgram(p, file)
                vm_file.save(self.compiler.compile(program))

    def __iter__(self) -> Iterator[str]:
        yield from File(self.path).load()

    """
    path: Path
    file_name: str
    compiler: JackCompiler = field(default_factory=DefaultCompiler.create)

    @classmethod
    def load_from(cls, file_or_directory_name: str) -> JackProgram:
        return cls(Path(file_or_directory_name), file_or_directory_name)

    def compile(self) -> None:
        if os.path.isfile(self.file_name):
            dir_name = self.file_name.split(".")[-2]
            path_dir = Path(dir_name + ".xml")
            xml_file = File(path_dir)
            p = Path(self.file_name)
            program = JackProgram(p, self.file_name)
            xml_file.save(self.compiler.compile(program))
        elif os.path.isdir(self.file_name):
            in_files = glob.glob(self.file_name + "/*.jack")
            for file in in_files:
                dir_name = file.split(".")[-2]
                path_dir = Path(dir_name + ".xml")
                xml_file = File(path_dir)
                p = Path(file)
                program = JackProgram(p, file)
                xml_file.save(self.compiler.compile(program))

    def __iter__(self) -> Iterator[str]:
        yield from File(self.path).load()
    """


class JackCompiler(Protocol):  # pragma: no cover
    def compile(self, jack_code: Iterable[str]) -> Iterable[str]:
        pass
