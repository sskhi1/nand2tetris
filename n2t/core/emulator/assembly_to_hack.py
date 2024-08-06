from __future__ import annotations

from typing import Iterable


class CodeModule:
    comp_table = {
        "0": "0101010",
        "1": "0111111",
        "D": "0001100",
        "A": "0110000",
        "M": "1110000",
        "-1": "0111010",
        "!D": "0001101",
        "!A": "0110001",
        "!M": "1110001",
        "-D": "0001111",
        "-A": "0110011",
        "-M": "1110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "M+1": "1110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "M-1": "1110010",
        "D+A": "0000010",
        "A+D": "0000010",
        "D+M": "1000010",
        "M+D": "1000010",
        "D-A": "0010011",
        "D-M": "1010011",
        "A-D": "0000111",
        "M-D": "1000111",
        "D&A": "0000000",
        "A&D": "0000000",
        "D&M": "1000000",
        "M&D": "1000000",
        "D|A": "0010101",
        "A|D": "0010101",
        "D|M": "1010101",
        "M|D": "1010101",
    }

    dest_table = {
        None: "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "ADM": "111",
    }

    jump_table = {
        None: "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }

    def __init__(self) -> None:
        self.dest_table = self.dest_table
        self.jump_table = self.jump_table
        self.comp_table = self.comp_table

    def dest(self, mnemonic: str | None) -> str:
        if mnemonic in self.dest_table:
            return self.dest_table[mnemonic]
        else:
            raise BaseException("Error while finding mnemonic")

    def comp(self, mnemonic: str | None) -> str:
        if mnemonic in self.comp_table:
            return self.comp_table[mnemonic]
        else:
            raise BaseException("Error while finding mnemonic")

    def jump(self, mnemonic: str | None) -> str:
        if mnemonic in self.jump_table:
            return self.jump_table[mnemonic]
        else:
            raise BaseException("Error while finding mnemonic")


class SymbolTable:
    symbol_table = {
        "R0": 0,
        "R1": 1,
        "R2": 2,
        "R3": 3,
        "R4": 4,
        "R5": 5,
        "R6": 6,
        "R7": 7,
        "R8": 8,
        "R9": 9,
        "R10": 10,
        "R11": 11,
        "R12": 12,
        "R13": 13,
        "R14": 14,
        "R15": 15,
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
        "SCREEN": 16384,
        "KBD": 24576,
    }

    def __init__(self) -> None:
        self.symbol_table = self.symbol_table

    def contains(self, symbol: str) -> bool:
        if symbol in self.symbol_table:
            return True
        else:
            return False

    def add_entry(self, symbol: str, address: int) -> None:
        if not self.contains(symbol):
            self.symbol_table[symbol] = address

    def get_address(self, symbol: str) -> int:
        if symbol in self.symbol_table:
            return self.symbol_table[symbol]
        else:
            raise BaseException("Error while finding symbol")


A_COMMAND = 0
C_COMMAND = 1
L_COMMAND = 2


class LineInfo:
    def __init__(self, current_line: str) -> None:
        self.current = current_line

    def command_type(self) -> int:
        if self.current[0] == "@":
            return A_COMMAND
        elif self.current[0] == "(":
            return L_COMMAND
        else:
            return C_COMMAND

    def symbol(self) -> str:
        if self.command_type() == A_COMMAND:
            return self.current[1:]
        elif self.command_type() == L_COMMAND:
            return self.current[1:-1]
        return ""

    def dest(self) -> str | None:
        if self.command_type() == C_COMMAND:
            if "=" in self.current:
                pair = self.current.split("=")
                return pair[0]
            else:
                return None
        else:
            raise BaseException("Error, not correct type of command")

    def comp(self) -> str | None:
        if self.command_type() == C_COMMAND:
            if "=" in self.current and ";" in self.current:
                three = self.current.split("=")
                pair = three[1].strip()
                result = pair.split(";")[0].strip()
                return result
            elif "=" in self.current:
                pair = self.current.split("=")[1]
                return pair.strip()
            elif ";" in self.current:
                pair = self.current.split(";")[0]
                return pair.strip()
            else:
                return None
        else:
            raise BaseException("Error, not correct type of command")

    def jump(self) -> str | None:
        if self.command_type() == C_COMMAND:
            if ";" in self.current:
                pair = self.current.split(";")
                return pair[-1].strip()
            else:
                return None
        else:
            raise BaseException("Error, not correct type of command")


def assemble(assembly: Iterable[str]) -> Iterable[str]:
    result = []

    assembly_list = []
    for line in assembly:
        if not line:
            continue
        comment_index = line.find("//")
        if comment_index != -1:
            line = line[:comment_index]
        line = line.strip()
        if line == "":
            continue
        assembly_list.append(line)

    symbols = SymbolTable()
    code = CodeModule()
    idx = 0
    added_symbols = []
    for line in assembly_list:
        parser = LineInfo(line)
        if parser.command_type() == L_COMMAND:
            symbols.add_entry(parser.symbol(), idx)
            added_symbols.append(parser.symbol())
            continue
        idx += 1
    idx = 16
    for line in assembly_list:
        line_info = LineInfo(line)

        if line_info.command_type() == C_COMMAND:
            c = line_info.comp()
            d = line_info.dest()
            j = line_info.jump()
            comp = str(code.comp(c))
            dest = str(code.dest(d))
            jump = str(code.jump(j))
            res = "111" + comp + dest + jump
            result.append(res)
        elif line_info.command_type() == A_COMMAND:
            symbol = line_info.symbol()
            if symbols.contains(symbol):
                address = symbols.get_address(symbol)
            else:
                if symbol.isdigit():
                    address = int(symbol)
                else:
                    symbols.add_entry(symbol, idx)
                    address = idx
                    idx += 1
            binary_address = format(address, "b")
            zeros_left = 16 - len(binary_address)
            res = ""
            for i in range(zeros_left):
                res += "0"
            res += binary_address
            result.append(res)
    for symbol in added_symbols:
        symbols.symbol_table.pop(symbol)
    return result
