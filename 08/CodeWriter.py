"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

from Parser import C_PUSH, C_POP, C_ARITHMETIC
CONST = 'constant'
POINTER = 'pointer'
STATIC = 'static'
TEMP = 'temp'
REAL_SEGMENTS = {
    'local': 'LCL',
    'argument': 'ARG',
    'this': 'THIS',
    'that': 'THAT'
}

TRUE = -1
FALSE = 0

POP_2_AND_PUSH_D = [
    "@SP",
    "M=M-1",
    "A=M-1",
    "M=D"
]

class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.__output_stream = output_stream
        self.__filename = ''
        self.__compare_num = 0
        self.__return_num = 1

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.__filename = filename

    def __write_lines_with_separator(self, lines):
        self.__output_stream.writelines((l + '\n' for l in lines))

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        if command in ("add", "sub", "and", "or"):
            self.__write_two_arg(command)
        elif command in ("neg", "not"):
            self.__write_one_arg(command)
        else:
            self.__write_compare(command)
    
    def __write_two_arg(self, operator):
        op_line = {'add': 'M+D', 'sub': 'M-D', 'and': 'M&D', 'or': 'M|D'}
        """Writes instructions for the add command
        """        
        lines = [
            "@SP",
            "A=M-1",
            "D=M",
            "A=A-1",
            f"D={op_line[operator]}"
        ] + POP_2_AND_PUSH_D
        self.__write_lines_with_separator(lines)

    def __write_one_arg(self, operator):
        op_line = {'not': '!M', 'neg': '-M'}
        lines = [
            "@SP",
            "A=M-1",
            f"M={op_line[operator]}"
        ]
        self.__write_lines_with_separator(lines)

    def __write_compare(self, comparison: str):
        comparison = comparison.upper() # Return EQ, LT, GT
        lines = [
            "@SP",
            "A=M-1",
            "D=M",
            "A=A-1",
            "D=M-D",
            f"@CMP_{self.__compare_num}_TRUE",
            f"D;J{comparison}",
            f"// Comparison {self.__compare_num} false",
            f"D={FALSE}",
            f"@CMP_{self.__compare_num}_END",
            "0;JMP",
            f"(CMP_{self.__compare_num}_TRUE)",
            f"D={TRUE}",
            f"(CMP_{self.__compare_num}_END)"
        ] + POP_2_AND_PUSH_D
        self.__write_lines_with_separator(lines)
        self.__compare_num += 1

    def write_bootstrap(self):
        self.__write_lines_with_separator([
            "// SP = 256",
            "@256",
            "D=A",
            "@SP",
            "M=D"
        ])
        self.write_call("Sys.init", 0)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to static i appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        if command == C_PUSH:
            self.__write_push(segment, index)
        elif command == C_POP:
            self.__write_pop(segment, index)

    def __write_push(self, segment: str, index: int):
        lines = []
        if segment == CONST:
            lines = [
                f"@{index}",
                "D=A"
                ]
        elif segment == POINTER:
            ptr = "THIS" if index == 0 else "THAT"
            lines = [
                f"@{ptr}",
                "D=M"
            ]
        elif segment == STATIC:
            lines = [
                f"@{self.__filename}.{index}",
                "D=M"
            ]
        elif segment == TEMP:
            lines = [
                f"@{5 + index}",
                "D=M"
            ]
        else:
            lines = [
                f"@{index}",
                "D=A",
                f"@{REAL_SEGMENTS[segment]}",
                "A=D+M",
                "D=M"
            ]
        lines.extend([
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ])
        self.__write_lines_with_separator(lines)

    def __write_pop(self, segment: str, index: int):
        if segment in REAL_SEGMENTS:
            self.__write_pop_dynamic_segments(segment, index)
        else:
            self.__write_pop_non_dynamic_segments(segment, index)

    def __write_pop_non_dynamic_segments(self, segment: str, index: int):
        lines = [
            "// Non Dynamic pop",
            "@SP",
            "A=M-1",
            "D=M",
        ]
        if segment == POINTER:
            ptr = "THIS" if index == 0 else "THAT"
            lines.append(f"@{ptr}")
        elif segment == STATIC:
            lines.append(f"@{self.__filename}.{index}")
        elif segment == TEMP:
            lines.append(f"@{5 + index}")
        lines.extend([
            "M=D",
            "@SP",
            "M=M-1"])
        self.__write_lines_with_separator(lines)

    def __write_pop_dynamic_segments(self, segment: str, index: int):
        lines = [
            "// Dynamic pop",
            f"@{index}",
            "D=A",
            f"@{REAL_SEGMENTS[segment]}",
            "D=D+M",
            "@R13", # Temporarily store requested address
            "M=D",
            "@SP",
            "A=M-1",
            "D=M",
            "@R13",
            "A=M",
            "M=D",
            "@SP",
            "M=M-1"
        ]
        self.__write_lines_with_separator(lines)

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        self.__write_lines_with_separator([f"({self.__filename}${label})"])
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        self.__write_lines_with_separator([
            f"@{self.__filename}${label}",
            "0;JMP"
        ])
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        self.__write_lines_with_separator([
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            f"@{self.__filename}${label}",
            "D;JNE"
        ])
    
    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        self.__write_lines_with_separator([f"({self.__filename}.{function_name})"])
        for _ in range(n_vars):
            self.__write_push("constant", 0)

    
    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "foo" be a function within the file Xxx.vm.
        The handling of each "call" command within foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        return_label = f"{self.__filename}$ret.{self.__return_num}"
        self.__return_num += 1
        
        def __push_label(ptr: str):
            self.__write_lines_with_separator([
                f"// push {ptr}",
                f"@{ptr}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])
        
        self.__write_lines_with_separator([
                f"// push return_addr",
                f"@{return_label}",
                "D=A",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
        ])
        __push_label("LCL")
        __push_label("ARG")
        __push_label("THIS")
        __push_label("THAT")
        self.__write_lines_with_separator([
                "// ARG = SP - 5 - n_args",
                f"@{5 + n_args}",
                "D=A",
                "@SP",
                "D=M-D",
                "@ARG",
                "M=D",
                "// LCL = SP",
                "@SP",
                "D=M",
                "@LCL",
                "M=D",
                f"// goto {function_name}",
                f"@{function_name}",
                "0;JMP",
                f"({return_label})"
            ])

    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        ENDFRAME = "R13"
        def __restore_label_from_endframe(label: str, distance: int):
            self.__write_lines_with_separator([
                f"// {label} = *(ENDFRAME - {distance})",
                f"@{distance}",
                "D=A",
                f"@{ENDFRAME}",
                "A=M-D",
                "D=M",
                f"@{label}",
                "M=D"
            ])

        self.__write_lines_with_separator([
            "// ENDFRAME = LCL",
            "@LCL",
            "D=M",
            f"@{ENDFRAME}",
            "M=D",
            "// *ARG = pop()",
            "@SP",
            "A=M-1",
            "D=M",
            "@ARG",
            "A=M",
            "M=D",
            "// SP = ARG + 1",
            "@ARG",
            "D=M",
            "@SP",
            "M=D+1",
        ])
        __restore_label_from_endframe("THAT", 1)
        __restore_label_from_endframe("THIS", 2)
        __restore_label_from_endframe("ARG", 3)
        __restore_label_from_endframe("LCL", 4)
        self.__write_lines_with_separator([
            "// goto *(ENDFRAME - 5)",
            f"@5",
            "D=A",
            f"@{ENDFRAME}",
            "A=M-D",
            "A=M",
            "0;JMP"
        ])