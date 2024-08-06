from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable

KEYWORD = 0
SYMBOL = 1
IDENTIFIER = 2
INT_CONST = 3
STRING_CONST = 4

KEYWORDS = [
    "class",
    "constructor",
    "function",
    "method",
    "field",
    "static",
    "var",
    "int",
    "char",
    "boolean",
    "void",
    "true",
    "false",
    "null",
    "this",
    "let",
    "do",
    "if",
    "else",
    "while",
    "return",
]

SYMBOLS = [
    "{",
    "}",
    "(",
    ")",
    "[",
    "]",
    ".",
    ",",
    ";",
    "+",
    "-",
    "*",
    "/",
    "&",
    "|",
    "<",
    ">",
    "=",
    "~",
]

EXPR_OPS = ["+", "-", "*", "/", "&", "|", "<", ">", "="]

STATEMENTS = ["do", "let", "while", "return", "if"]

COMPARATOR = ["<", ">", "&"]


class SymbolTable:
    def __init__(self) -> None:
        self.next_index = {"static": 0, "this": 0, "argument": 0, "local": 0}
        self.class_table: Dict[str, Any] = {}
        self.subroutine_table: Dict[str, Any] = {}

    def define(self, name: str, type: str, kind: str) -> None:
        kind = kind if kind != "field" else "this"
        if kind == "static" or kind == "this":
            self.class_table[name] = (type, kind, self.var_count(kind))
            self.next_index[kind] += 1
        elif kind in ["local", "argument"]:
            self.class_table[name] = (type, kind, self.var_count(kind))
            self.next_index[kind] += 1

    def __contains__(self, name: str) -> bool:
        return self.get_row_by_name(name) is not None

    def start_subroutine(self) -> None:
        self.subroutine_table = {}
        self.next_index["local"] = 0
        self.next_index["argument"] = 0

    def var_count(self, kind: str) -> int:
        return self.next_index[kind]

    def kind_of(self, name: str) -> str | None:
        entry = self.get_row_by_name(name)
        return entry[1] if entry else None

    def type_of(self, name: str) -> str | None:
        entry = self.get_row_by_name(name)
        return entry[0] if entry else None

    def index_of(self, name: str) -> int | None:
        entry = self.get_row_by_name(name)
        return entry[2] if entry else None

    def get_row_by_name(self, name: str) -> Any:
        if name in self.subroutine_table:
            return self.subroutine_table[name]
        elif name in self.class_table:
            return self.class_table[name]
        return None


class VMWriter:
    def __init__(self) -> None:
        self.unique_counter = 0

    def write_push(self, segment: Any, index: Any) -> list[str]:
        return [f"push {segment} {index}"]

    def write_pop(self, segment: Any, index: Any) -> list[str]:
        return [f"pop {segment} {index}"]

    def write_arithmetic(self, command: str) -> list[str]:
        return [f"{command}"]

    def write_label(self, label: str) -> list[str]:
        return [f"label {label}"]

    def write_goto(self, label: str) -> list[str]:
        return [f"goto {label}"]

    def write_if_goto(self, label: str) -> list[str]:
        return [f"if-goto {label}"]

    def write_call(self, name: str, args_num: Any) -> list[str]:
        return [f"call {name} {args_num}"]

    def write_function(self, name: str, locals_num: Any) -> list[str]:
        return [f"function {name} {locals_num}"]

    def write_return(self) -> list[str]:
        return ["return"]


class WordInfo:
    def __init__(self, current_word: str) -> None:
        self.word = current_word

    def token_type(self) -> int:
        if self.word in KEYWORDS:
            return KEYWORD
        elif self.word in SYMBOLS:
            return SYMBOL
        elif self.word[0] == '"':
            return STRING_CONST
        elif self.word.isnumeric():
            return INT_CONST
        else:
            return IDENTIFIER

    def keyword(self) -> str:
        if self.word in KEYWORDS:
            return self.word
        else:
            raise BaseException("Error")

    def symbol(self) -> str:
        if self.word in SYMBOLS:
            if self.word in COMPARATOR:
                if self.word == ">":
                    return "&gt;"
                elif self.word == "<":
                    return "&lt;"
                elif self.word == "&":
                    return "&amp;"
            else:
                return self.word
            return ""
        else:
            raise BaseException("Error")

    def identifier(self) -> str:
        if self.token_type() == IDENTIFIER:
            return self.word
        else:
            raise BaseException("Error")

    def int_val(self) -> str:
        if self.token_type() == INT_CONST:
            return self.word
        else:
            raise BaseException("Error")

    def string_val(self) -> str:
        if self.token_type() == STRING_CONST:
            return self.word[1:-1]
        else:
            raise BaseException("Error")


def find_tokens(line: str) -> list[str]:
    result = []
    curr = ""
    i = 0
    while i < len(line):
        ch = line[i]
        if ch in SYMBOLS:
            result.append(ch)
            i += 1
        elif ch == '"':
            curr += ch
            i += 1
            ch = ""
            while not ch == '"':
                ch = line[i]
                curr += ch
                i += 1
            result.append(curr)
            curr = ""
        elif ch.isalpha():
            curr += ch
            i += 1
            while ch.isalpha() or ch.isdigit() or ch == "_":
                ch = line[i]
                if ch in SYMBOLS:
                    break
                curr += ch
                i += 1
            result.append(curr)
            curr = ""
        elif ch.isdigit():
            curr += ch
            i += 1
            while ch.isdigit():
                ch = line[i]
                if ch in SYMBOLS:
                    break
                curr += ch
                i += 1
            result.append(curr)
            curr = ""
        else:
            i += 1
    return result


def generate(word: str) -> str:
    w = WordInfo(word)
    res = ""
    if w.token_type() == SYMBOL:
        res += "<symbol> "
        res += w.symbol()
        res += " </symbol>"
    elif w.token_type() == KEYWORD:
        res += "<keyword> "
        res += w.keyword()
        res += " </keyword>"
    elif w.token_type() == INT_CONST:
        res += "<integerConstant> "
        res += w.int_val()
        res += " </integerConstant>"
    elif w.token_type() == STRING_CONST:
        res += "<stringConstant> "
        res += w.string_val()
        res += " </stringConstant>"
    elif w.token_type() == IDENTIFIER:
        res += "<identifier> "
        res += w.identifier()
        res += " </identifier>"
    return res


class CompilationEngine:
    def __init__(self, tokens: list[str]):
        self.subroutine_name = ""
        self.subroutine_type = ""
        self.i = 0
        self.tokens = tokens
        self.vm_writer = VMWriter()
        self.symbol_table = SymbolTable()
        self.counter = 0
        self.class_name = ""
        self.math_mappings = {
            "+": "add",
            "-": "sub",
            "*": "Math.multiply",
            "/": "Math.divide",
            "&": "and",
            "|": "or",
            "<": "lt",
            ">": "gt",
            "=": "eq",
        }

    def compile_class(self) -> list[str]:
        result = []
        self.i += 1
        curr = self.tokens[self.i]
        self.class_name = curr
        self.i += 1
        self.i += 1
        curr = self.tokens[self.i]
        while curr == "static" or curr == "field":
            self.compile_class_var_dec()
            self.i += 1
            curr = self.tokens[self.i]

        while curr == "constructor" or curr == "function" or curr == "method":
            result += self.compile_subroutine()
            self.i += 1
            curr = self.tokens[self.i]
        return result

    def compile_class_var_dec(self) -> None:
        kind = self.tokens[self.i]
        self.i += 1
        type = self.tokens[self.i]
        curr = type
        while True:
            self.i += 1
            self.symbol_table.define(self.tokens[self.i], type, kind)
            self.i += 1
            curr = self.tokens[self.i]
            if curr != ",":
                break

    def compile_subroutine(self) -> list[str]:
        result = []
        self.symbol_table.start_subroutine()
        self.subroutine_type = self.tokens[self.i]
        if self.subroutine_type == "method":
            self.symbol_table.define("this", self.class_name, "argument")
        self.i += 1
        self.i += 1
        self.subroutine_name = self.tokens[self.i]
        self.i += 1
        self.i += 1
        self.compile_parameter_list()
        self.i += 1
        self.i += 1
        local_vars = 0
        curr = self.tokens[self.i]
        while curr == "var":
            local_vars += self.compile_var_dec()
            self.i += 1
            curr = self.tokens[self.i]
        result += self.vm_writer.write_function(
            self.class_name + "." + self.subroutine_name, local_vars
        )
        if self.subroutine_type == "method":
            result += self.vm_writer.write_push("argument", 0)
            result += self.vm_writer.write_pop("pointer", 0)
        elif self.subroutine_type == "constructor":
            result += self.vm_writer.write_push(
                "constant", self.symbol_table.var_count("this")
            )
            result += self.vm_writer.write_call("Memory.alloc", 1)
            result += self.vm_writer.write_pop("pointer", 0)
        result += self.compile_statements()
        return result

    def compile_parameter_list(self) -> None:
        curr = self.tokens[self.i]
        while curr != ")":
            info = WordInfo(curr)
            type = info.token_type()
            self.i += 1
            curr = self.tokens[self.i]
            self.symbol_table.define(curr, str(type), "argument")
            self.i += 1
            curr = self.tokens[self.i]
            if curr == ",":
                self.i += 1
                curr = self.tokens[self.i]

    def compile_var_dec(self) -> int:
        var_num = 0
        self.i += 1
        curr = self.tokens[self.i]
        type = curr
        while curr != ";":
            var_num += 1
            self.i += 1
            curr = self.tokens[self.i]
            var_name = curr
            self.symbol_table.define(var_name, type, "local")
            self.i += 1
            curr = self.tokens[self.i]
        return var_num

    def compile_statements(self) -> list[str]:
        result = []
        curr = self.tokens[self.i]
        while curr in STATEMENTS:
            if curr == "do":
                result += self.compile_do()
            elif curr == "let":
                result += self.compile_let()
            elif curr == "while":
                result += self.compile_while()
            elif curr == "return":
                result += self.compile_return()
            elif curr == "if":
                result += self.compile_if()
            curr = self.tokens[self.i]
        return result

    def compile_subroutine_call(self) -> list[str]:
        name = self.tokens[self.i]
        self.i += 1
        result = []
        args_num = 1
        class_name: str = self.class_name
        curr = self.tokens[self.i]
        if curr == ".":
            if name not in self.symbol_table:
                args_num = 0
                class_name = name
            else:
                class_name = str(self.symbol_table.type_of(name))
                result += self.vm_writer.write_push(
                    self.symbol_table.kind_of(name), self.symbol_table.index_of(name)
                )
            self.i += 1
            curr = self.tokens[self.i]
            name = curr
            self.i += 1
            curr = self.tokens[self.i]
        else:
            result += self.vm_writer.write_push("pointer", 0)
        subroutine_name = class_name + "." + name
        self.i += 1
        tmp = self.compile_expression_list()
        args_num += tmp[1]
        result += tmp[0]
        result += self.vm_writer.write_call(subroutine_name, args_num)
        self.i += 1
        return result

    def compile_do(self) -> list[str]:
        result = []
        self.i += 1
        result += self.compile_subroutine_call()
        result += self.vm_writer.write_pop("temp", 0)
        self.i += 1
        return result

    def compile_let(self) -> list[str]:
        result = []
        self.i += 1
        var_name = self.tokens[self.i]
        self.i += 1
        curr = self.tokens[self.i]
        if curr == "[":
            self.i += 1
            curr = self.tokens[self.i]
            result += self.vm_writer.write_push(
                self.symbol_table.kind_of(var_name),
                self.symbol_table.index_of(var_name),
            )
            result += self.compile_expression()
            result += self.vm_writer.write_arithmetic("add")
            self.i += 1
            self.i += 1
            result += self.compile_expression()
            result += self.vm_writer.write_pop("temp", 0)
            result += self.vm_writer.write_pop("pointer", 1)
            result += self.vm_writer.write_push("temp", 0)
            result += self.vm_writer.write_pop("that", 0)
        else:
            self.i += 1
            result += self.compile_expression()
            result += self.vm_writer.write_pop(
                self.symbol_table.kind_of(var_name),
                self.symbol_table.index_of(var_name),
            )
        self.i += 1
        return result

    def compile_while(self) -> list[str]:
        result = []
        while1 = "WHILE_EXP" + str(self.counter)
        while2 = "WHILE_END" + str(self.counter)
        self.counter += 1
        self.i += 1
        self.i += 1
        result += self.vm_writer.write_label(while1)
        result += self.compile_expression()
        result += self.vm_writer.write_arithmetic("not")
        result += self.vm_writer.write_if_goto(while2)
        self.i += 1
        self.i += 1
        result += self.compile_statements()
        result += self.vm_writer.write_goto(while1)
        result += self.vm_writer.write_label(while2)
        self.i += 1
        return result

    def compile_return(self) -> list[str]:
        result = []
        self.i += 1
        curr = self.tokens[self.i]
        if curr == ";":
            result += self.vm_writer.write_push("constant", 0)
        else:
            result += self.compile_expression()
        result += self.vm_writer.write_return()
        self.i += 1
        return result

    def compile_if(self) -> list[str]:
        result = []
        if1 = "IF_TRUE" + str(self.counter)
        if2 = "IF_FALSE" + str(self.counter)
        self.counter += 1
        self.i += 1
        curr = self.tokens[self.i]
        self.i += 1
        curr = self.tokens[self.i]
        result += self.compile_expression()
        result += self.vm_writer.write_arithmetic("not")
        self.i += 1
        curr = self.tokens[self.i]
        self.i += 1
        curr = self.tokens[self.i]
        result += self.vm_writer.write_if_goto(if1)
        result += self.compile_statements()
        result += self.vm_writer.write_goto(if2)
        self.i += 1
        curr = self.tokens[self.i]
        result += self.vm_writer.write_label(if1)
        curr = self.tokens[self.i]
        if curr == "else":
            self.i += 1
            curr = self.tokens[self.i]
            self.i += 1
            curr = self.tokens[self.i]
            result += self.compile_statements()
            self.i += 1
            curr = self.tokens[self.i]
        result += self.vm_writer.write_label(if2)
        return result

    def compile_expression(self) -> list[str]:
        result = []
        result += self.compile_term()
        curr = self.tokens[self.i]
        while curr in EXPR_OPS:
            operator = curr
            self.i += 1
            curr = self.tokens[self.i]
            result += self.compile_term()
            command = self.math_mappings[operator]
            if operator in ["*", "/"]:
                result += self.vm_writer.write_call(command, 2)
            else:
                result += self.vm_writer.write_arithmetic(command)
        return result

    def compile_term(self) -> list[str]:
        result = []
        curr = self.tokens[self.i]
        w = WordInfo(curr)
        if curr == "(":
            self.i += 1
            curr = self.tokens[self.i]
            result += self.compile_expression()
            self.i += 1
            curr = self.tokens[self.i]
        elif curr == "-" or curr == "~":
            self.i += 1
            curr = self.tokens[self.i]
            result += self.compile_term()
            arithmetic = "neg" if curr == "-" else "not"
            result += self.vm_writer.write_arithmetic(arithmetic)
        elif w.token_type() == IDENTIFIER:
            result += self.compile_term_identifier()
        elif (
            w.token_type() == INT_CONST
            or w.token_type() == STRING_CONST
            or w.token_type() == KEYWORD
        ):
            result += self.compile_term_constants()
        return result

    def compile_term_constants(self) -> list[str]:
        result = []
        curr = self.tokens[self.i]
        info = WordInfo(curr)
        if info.token_type() == INT_CONST:
            result += self.vm_writer.write_push("constant", curr)
        elif info.token_type() == KEYWORD:
            if curr == "this":
                result += self.vm_writer.write_push("pointer", 0)
            elif curr == "true":
                result += self.vm_writer.write_push("constant", 0)
                result += self.vm_writer.write_arithmetic("not")
            else:
                result += self.vm_writer.write_push("constant", 0)
        else:
            curr = curr[1:-1]
            length = len(curr)
            result += self.vm_writer.write_push("constant", length)
            result += self.vm_writer.write_call("String.new", 1)
            for char in curr:
                result += self.vm_writer.write_push("constant", ord(char))
                result += self.vm_writer.write_call("String.appendChar", 2)
        self.i += 1
        return result

    def compile_term_identifier(self) -> list[str]:
        result = []
        self.i += 1
        curr = self.tokens[self.i]
        if curr == "[":
            var_name = self.tokens[self.i - 1]
            result += self.vm_writer.write_push(
                self.symbol_table.kind_of(var_name),
                self.symbol_table.index_of(var_name),
            )
            self.i += 1
            curr = self.tokens[self.i]
            result += self.compile_expression()
            result += self.vm_writer.write_arithmetic("add")
            result += self.vm_writer.write_pop("pointer", 1)
            result += self.vm_writer.write_push("that", 0)
            self.i += 1
            curr = self.tokens[self.i]
        elif curr == "(" or curr == ".":
            self.i -= 1
            result += self.compile_subroutine_call()
        else:
            var_name = self.tokens[self.i - 1]
            segment = self.symbol_table.kind_of(var_name)
            index = self.symbol_table.index_of(var_name)
            result += self.vm_writer.write_push(segment, index)
        return result

    def compile_expression_list(self) -> tuple[list[Any], int]:
        result = []
        args_num = 0
        curr = self.tokens[self.i]
        while curr != ")":
            args_num += 1
            result += self.compile_expression()
            curr = self.tokens[self.i]
            if curr == ",":
                self.i += 1
                curr = self.tokens[self.i]
        return result, args_num


@dataclass
class JackCompiler:
    @classmethod
    def create(cls) -> JackCompiler:
        return cls()

    def compile(self, jack_code: Iterable[str]) -> Iterable[str]:
        tokens = []
        # result = ["<tokens>"]
        for line in jack_code:
            stripped_line = line.strip()
            if not stripped_line:
                continue
            if (
                stripped_line[0] == "*"
                or stripped_line[0:2] == "//"
                or stripped_line[0:2] == "/*"
            ):
                continue
            comment_index = stripped_line.find("//")
            if comment_index != -1:
                stripped_line = stripped_line[:comment_index]
            stripped_line = stripped_line.strip()
            if not stripped_line:
                continue
            comment_index = stripped_line.find("/*")
            if comment_index != -1:
                stripped_line = stripped_line[:comment_index]
            stripped_line = stripped_line.strip()
            if not stripped_line:
                continue
            tokens_list = find_tokens(stripped_line)
            list_stripped = []
            for word in tokens_list:
                list_stripped.append(word.strip())
            tokens += list_stripped
        ce = CompilationEngine(tokens)
        result = ce.compile_class()
        # result.append("</tokens>")
        return result
