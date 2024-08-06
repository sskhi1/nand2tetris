from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List

C_ARITHMETIC = 1
C_PUSH = 2
C_POP = 3
C_LABEL = 4
C_IF_GOTO = 5
C_GOTO = 6
C_FUNCTION = 7
C_RETURN = 8
C_CALL = 9

compare_index = 0
call_index = 0


class LineInfo:
    def __init__(self, line: str, file_name: str):
        self.current = ""
        self.parts: List[str] = []
        self.parts = line.split(" ")
        self.file_name = file_name

    def get_file_name(self) -> str:
        return self.file_name

    def arg1(self) -> Any:
        if len(self.parts) == 0:
            return None
        return self.parts[0]

    def arg2(self) -> Any:
        if len(self.parts) < 2:
            return None
        return self.parts[1]

    def arg3(self) -> None | int:
        if len(self.parts) < 3:
            return None
        return int(self.parts[2])

    def command_type(self) -> int:
        if self.arg1() == "push":
            return C_PUSH
        elif self.arg1() == "pop":
            return C_POP
        elif (
            self.arg1() == "add"
            or self.arg1() == "sub"
            or self.arg1() == "neg"
            or self.arg1() == "eq"
            or self.arg1() == "lt"
            or self.arg1() == "gt"
            or self.arg1() == "and"
            or self.arg1() == "or"
            or self.arg1() == "not"
        ):
            return C_ARITHMETIC
        elif self.arg1() == "label":
            return C_LABEL
        elif self.arg1() == "goto":
            return C_GOTO
        elif self.arg1() == "if-goto":
            return C_IF_GOTO
        elif self.arg1() == "function":
            return C_FUNCTION
        elif self.arg1() == "call":
            return C_CALL
        elif self.arg1() == "return":
            return C_RETURN
        else:
            return -1


VM_Segments_Stack = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
}


def push_command(parser: LineInfo) -> str:
    result = ""
    ending = "@SP A=M M=D @SP M=M+1"
    if parser.arg2() == "constant":
        result = "@" + str(parser.arg3()) + " D=A " + ending
    elif parser.arg2() == "static":
        result = "@" + parser.get_file_name() + str(parser.arg3()) + " D=M " + ending
    elif parser.arg2() == "temp":
        result = "@" + str(parser.arg3()) + " D=A @5" + " A=A+D D=M " + ending
    elif parser.arg2() in VM_Segments_Stack:
        result = (
            "@"
            + str(parser.arg3())
            + " D=A @"
            + str(VM_Segments_Stack[parser.arg2()])
            + " A=M+D "
            "D=M " + ending
        )
    elif parser.arg2() == "pointer":
        result = "@" + str(parser.arg3()) + " D=A @3 A=A+D D=M " + ending
    return result


def pop_command(parser: LineInfo) -> str:
    result = ""
    ending = " D=D+A @R13 M=D @SP M=M-1 A=M D=M @R13 A=M M=D"
    if parser.arg2() == "static":
        result = (
            "@SP M=M-1 A=M D=M @" + parser.get_file_name() + str(parser.arg3()) + " M=D"
        )
    elif parser.arg2() == "temp":
        result = "@" + str(parser.arg3()) + " D=A @5" + ending
    elif parser.arg2() in VM_Segments_Stack:
        result = (
            "@"
            + str(parser.arg3())
            + " D=A @"
            + VM_Segments_Stack[parser.arg2()]
            + " A=M"
            + ending
        )
    elif parser.arg2() == "pointer":
        result = "@" + str(parser.arg3()) + " D=A @3" + ending
    return result


def arithmetic_command(parser: LineInfo, compare_index: int) -> str:
    result = ""
    if parser.arg1() == "neg":
        result = "@SP A=M-1 M=-M"
    elif parser.arg1() == "not":
        result = "@SP A=M-1 M=!M"
    elif parser.arg1() == "add":
        result = "@SP M=M-1 A=M D=M A=A-1 M=M+D"
    elif parser.arg1() == "and":
        result = "@SP M=M-1 A=M D=M A=A-1 M=M&D"
    elif parser.arg1() == "sub":
        result = "@SP M=M-1 A=M D=M A=A-1 M=M-D"
    elif parser.arg1() == "or":
        result = "@SP M=M-1 A=M D=M A=A-1 M=M|D"
    elif parser.arg1() == "eq":
        result = (
            "@SP M=M-1 A=M D=M A=A-1 D=M-D @EQUALS"
            + str(compare_index)
            + " D;JEQ @SP A=M-1 M=0 @END"
            + str(compare_index)
            + " 0;JMP (EQUALS"
            + str(compare_index)
            + ") @SP A=M-1 M=-1 (END"
            + str(compare_index)
            + ")"
        )
    elif parser.arg1() == "lt":
        result = (
            "@SP M=M-1 A=M D=M A=A-1 D=M-D @LESS"
            + str(compare_index)
            + " D;JLT @SP A=M-1 M=0 @END"
            + str(compare_index)
            + " 0;JMP (LESS"
            + str(compare_index)
            + ") @SP A=M-1 M=-1 (END"
            + str(compare_index)
            + ")"
        )
    elif parser.arg1() == "gt":
        result = (
            "@SP M=M-1 A=M D=M A=A-1 D=M-D @GREATER"
            + str(compare_index)
            + " D;JGT @SP A=M-1 M=0 @END"
            + str(compare_index)
            + " 0;JMP (GREATER"
            + str(compare_index)
            + ") @SP A=M-1 M=-1 (END"
            + str(compare_index)
            + ")"
        )
    return result


def function_command(parser: LineInfo) -> str:
    result = "(" + parser.arg2() + ")"
    num = int(str(parser.arg3()))
    for i in range(num):
        result += " @SP A=M M=0 @SP M=M+1"
    return str(result)


def call_command(parser: LineInfo, call_index: int) -> str:
    result = ""
    c_name = "CALL_LABEL" + str(call_index)
    result += "@" + c_name + " D=A @SP A=M M=D @SP M=M+1 "
    result += "@LCL D=M @SP A=M M=D @SP M=M+1 "
    result += "@ARG D=M @SP A=M M=D @SP M=M+1 "
    result += "@THIS D=M @SP A=M M=D @SP M=M+1 "
    result += "@THAT D=M @SP A=M M=D @SP M=M+1 "
    result += "@SP D=M @5 D=D-A @" + str(parser.arg3()) + " D=D-A @ARG M=D "
    result += "@SP D=M @LCL M=D "
    result += "@" + parser.arg2() + " 0;JMP "
    result += "(" + c_name + ")"
    return result


def return_command() -> str:
    result = ""
    result += "@LCL D=M @R13 M=D "
    result += "@5 D=A @R13 D=M-D A=D D=M @R14 M=D "
    result += "@SP A=M-1 D=M @ARG A=M M=D "
    result += "@ARG D=M @SP M=D+1 "
    result += "@R13 M=M-1 A=M D=M @THAT M=D "
    result += "@R13 M=M-1 A=M D=M @THIS M=D "
    result += "@R13 M=M-1 A=M D=M @ARG M=D "
    result += "@R13 M=M-1 A=M D=M @LCL M=D "
    result += "@R14 A=M 0;JMP"
    return result


def translate_file(vm_code: Iterable[str], file_name: str) -> list[str]:
    global compare_index
    global call_index
    result = []
    for line in vm_code:
        if not line:
            continue
        comment_index = line.find("//")
        if comment_index != -1:
            line = line[:comment_index]
        line = line.strip()
        parser = LineInfo(line, file_name)
        current_result = ""
        if parser.command_type() == C_POP:
            current_result += "//pop "
            current_result += pop_command(parser)
        elif parser.command_type() == C_PUSH:
            current_result += "//push "
            current_result += push_command(parser)
        elif parser.command_type() == C_ARITHMETIC:
            compare_index += 1
            current_result += "//arithmetic "
            current_result += arithmetic_command(parser, compare_index)
        elif parser.command_type() == C_LABEL:
            current_result += "//label "
            current_result += "(" + parser.arg2() + ")"
        elif parser.command_type() == C_GOTO:
            current_result += "//goto "
            current_result += "@" + parser.arg2() + " 0;JMP"
        elif parser.command_type() == C_IF_GOTO:
            current_result += "//if-goto "
            current_result += "@SP M=M-1 A=M D=M @" + parser.arg2() + " D;JNE"
        elif parser.command_type() == C_CALL:
            call_index += 1
            current_result += "//call "
            current_result += call_command(parser, call_index)
        elif parser.command_type() == C_FUNCTION:
            current_result += "//function "
            current_result += function_command(parser)
        elif parser.command_type() == C_RETURN:
            current_result += "//return "
            current_result += return_command()

        result_in_array = current_result.split(" ")
        for asm_line in result_in_array:
            result.append(asm_line)
    return result


@dataclass
class VMTranslator:
    @classmethod
    def create(cls) -> VMTranslator:
        return cls()

    def translate(
        self, vm_code: Iterable[str], file_name: str, is_dir: bool
    ) -> Iterable[str]:
        global compare_index
        global call_index
        if is_dir:
            result = ["@256", "D=A", "@SP", "M=D"]
            call_index += 1
            res = ""
            c_name = "CALL_LABEL" + str(call_index)
            res += "@" + c_name + " D=A @SP A=M M=D @SP M=M+1 "
            res += "@LCL D=M @SP A=M M=D @SP M=M+1 "
            res += "@ARG D=M @SP A=M M=D @SP M=M+1 "
            res += "@THIS D=M @SP A=M M=D @SP M=M+1 "
            res += "@THAT D=M @SP A=M M=D @SP M=M+1 "
            res += "@SP D=M @5 D=D-A @0 D=D-A @ARG M=D "
            res += "@SP D=M @LCL M=D "
            res += "@Sys.init 0;JMP "
            res += "(" + c_name + ")"
            res_lst = res.split(" ")
            for line in res_lst:
                result.append(line)
            if vm_code:
                for infile in vm_code:
                    itr = []
                    curr_file_name = infile.split("\\")[-1]
                    f = open(infile, "r")
                    for x in f:
                        itr.append(x)
                    f.close()
                    result.extend(translate_file(itr, curr_file_name))
            return result
        else:
            file_name_short = file_name.split("\\")[-1]
            result = []
            result.extend(translate_file(vm_code, file_name_short))
            return result
