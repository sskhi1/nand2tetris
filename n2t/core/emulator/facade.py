from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple

from n2t.core.emulator.assembly_to_hack import assemble


def get_bit(bits: int, index: int) -> bool:
    return (bits >> index) & 1 == 1


def get_segment(number: int, start_bit: int, end_bit: int) -> int:
    mask = ~(-1 << (end_bit - start_bit + 1))
    return (number >> start_bit) & mask


def to_binary(val: int) -> str:
    return format(val, "016b")


def to_int(val: str) -> int:
    return int(val, 2)


def execute_alu(c_bits: int, x: int, y: int) -> Tuple[int, bool, bool]:
    x_tmp = x
    y_tmp = y

    zx, nx, zy, ny, f, no = (get_bit(c_bits, i) for i in range(5, -1, -1))

    if zx:
        x_tmp = 0

    if nx:
        x_tmp = (~x_tmp) & 0xFFFF

    if zy:
        y_tmp = 0

    if ny:
        y_tmp = (~y_tmp) & 0xFFFF

    if f:
        alu_output = (x_tmp + y_tmp) & 0xFFFF
    else:
        alu_output = (x_tmp & y_tmp) & 0xFFFF

    if no:
        alu_output = (~alu_output) & 0xFFFF

    zr = alu_output == 0
    ng = (alu_output & 0x8000) != 0
    return alu_output, zr, ng


def find_jump_result(j_value: int, zr: bool, ng: bool) -> bool:
    if j_value == 0:
        jump_result = False
    elif j_value == 1:
        jump_result = not (zr or ng)
    elif j_value == 2:
        jump_result = zr
    elif j_value == 3:
        jump_result = not ng
    elif j_value == 4:
        jump_result = ng
    elif j_value == 5:
        jump_result = not zr
    elif j_value == 6:
        jump_result = ng or zr
    else:
        jump_result = True
    return jump_result


class Computer:
    def __init__(self) -> None:
        self.pc = 0
        self.ram = [0] * 65536
        self.rom = [-1] * 65536
        self.d_register = 0
        self.a_register = 0
        self.result: Dict[int, int] = {}

    def make_step(self) -> None | bool:
        line = self.rom[self.pc]
        if line == -1:
            return None

        if not get_bit(line, 15):
            return self.simulate_a_instruction(line)
        else:
            return self.simulate_c_instruction(line)

    def simulate_a_instruction(self, line: int) -> bool:
        self.a_register = get_segment(line, 0, 14)
        self.pc += 1
        self.pc = self.pc & 0xFFFF
        return True

    def simulate_c_instruction(self, line: int) -> bool:
        a = self.d_register & 0xFFFF
        if get_bit(line, 12):
            b = self.ram[self.a_register] & 0xFFFF
        else:
            b = self.a_register & 0xFFFF

        c_bits = get_segment(line, 6, 11) & 0xFFFF
        (alu_output, zr, ng) = execute_alu(c_bits, a, b)

        d_bits = get_segment(line, 3, 5) & 0xFFFF
        self.d_bits_instruction(d_bits, alu_output)

        j_value = get_segment(line, 0, 2) & 0xFFFF
        jump_result = find_jump_result(j_value, zr, ng)

        if jump_result:
            self.pc = self.a_register & 0xFFFF
        else:
            self.pc += 1
            self.pc = self.pc & 0xFFFF
        return True

    def d_bits_instruction(self, d_bits: int, alu_output: int) -> None:
        if d_bits == 1:
            self.ram[self.a_register] = alu_output
            self.result[self.a_register] = alu_output
        elif d_bits == 2:
            self.d_register = alu_output
        elif d_bits == 3:
            self.ram[self.a_register] = alu_output
            self.d_register = alu_output
            self.result[self.a_register] = alu_output
        elif d_bits == 4:
            self.a_register = alu_output
        elif d_bits == 5:
            self.ram[self.a_register] = alu_output
            self.result[self.a_register] = alu_output
            self.a_register = alu_output
        elif d_bits == 6:
            self.a_register = alu_output
            self.d_register = alu_output
        elif d_bits == 7:
            self.ram[self.a_register] = alu_output
            self.result[self.a_register] = alu_output
            self.a_register = alu_output
            self.d_register = alu_output


def simulate_hack_with_cycles(hack_lines: Iterable[str], cycles: int) -> Iterable[str]:
    result = []
    computer = Computer()
    for i, line in enumerate(hack_lines, start=0):
        computer.rom[i] = to_int(line) & 0xFFFF

    for _ in range(cycles):
        has_more = computer.make_step()
        if has_more is None:
            break

    result_ram = computer.result
    sorted_result_ram = dict(sorted(result_ram.items()))
    dict_size = len(sorted_result_ram)
    i = 0
    for key, value in sorted_result_ram.items():
        i += 1
        if i == dict_size:
            result.append('        "' + str(key) + '": ' + str(value))
        else:
            result.append('        "' + str(key) + '": ' + str(value) + ",")

    return result


def simulate_hack_without_cycles(hack_lines: Iterable[str]) -> Iterable[str]:
    result = []
    computer = Computer()
    for i, line in enumerate(hack_lines, start=0):
        computer.rom[i] = to_int(line) & 0xFFFF

    while True:
        has_more = computer.make_step()
        if has_more is None:
            break

    result_ram = computer.result
    sorted_result_ram = dict(sorted(result_ram.items()))
    dict_size = len(sorted_result_ram)
    i = 0
    for key, value in sorted_result_ram.items():
        i += 1
        if i == dict_size:
            result.append('        "' + str(key) + '": ' + str(value))
        else:
            result.append('        "' + str(key) + '": ' + str(value) + ",")

    return result


def simulate_hack(hack_lines: Iterable[str], cycles: int) -> Iterable[str]:
    assert cycles >= -1
    if cycles >= 0:
        return simulate_hack_with_cycles(hack_lines, cycles)
    else:
        return simulate_hack_without_cycles(hack_lines)


def write_json(hack_lines: Iterable[str], cycles: int) -> Iterable[str]:
    result = ["{", '    "RAM": {']
    result += simulate_hack(hack_lines, cycles)
    result.append("    }")
    result.append("}")
    return result


def transfer_to_hack_lines(lines: Iterable[str], file_name: str) -> Iterable[str]:
    file_type = file_name.split(".")[-1]
    if file_type == "hack":
        return lines
    else:
        return assemble(lines)


@dataclass
class Emulator:
    @classmethod
    def create(cls) -> Emulator:
        return cls()

    def emulate(
        self, lines: Iterable[str], file_name: str, cycles: int
    ) -> Iterable[str]:
        hack_lines = transfer_to_hack_lines(lines, file_name)
        result = write_json(hack_lines, cycles)
        return result
