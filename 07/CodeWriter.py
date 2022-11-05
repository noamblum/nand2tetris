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
        self.__write_compare_start()
        self.__write_compare_same_sign(comparison)
        self.__write_compare_different_sign(comparison)
        self.__write_compare_end()
        self.__compare_num += 1

    def __write_compare_start(self):
        lines = [
            f"// Comparison {self.__compare_num} start",
            "// Check x >= 0",
            "@SP",
            "A=M-1",
            "A=A-1",
            "D=M",
            f"@CMP_{self.__compare_num}_X_NEG",
            "D;JLT",
            "// If here than x >= 0, check y >= 0",
            "@SP",
            "A=M-1",
            "D=M",
            f"@CMP_{self.__compare_num}_Y_NEG_X_POS",
            "D;JLT",
            "// If here than x >= 0 and y >= 0, goto same sign",
            f"@CMP_{self.__compare_num}_SAME_SIGN",
            "0;JMP",
            f"(CMP_{self.__compare_num}_X_NEG)",
            "// If here than x < 0, check y < 0",
            "@SP",
            "A=M-1",
            "D=M",
            f"@CMP_{self.__compare_num}_Y_POS_X_NEG",
            "D;JGE",
            "// If here than x < 0 and y < 0, goto same sign",
            f"@CMP_{self.__compare_num}_SAME_SIGN",
            "0;JMP",   
        ]
        self.__write_lines_with_separator(lines)

    def __write_compare_end(self):
        lines = [
            f"(CMP_{self.__compare_num}_FALSE)",
            f"D={FALSE}",
            f"@CMP_{self.__compare_num}_END",
            "0;JMP",
            f"(CMP_{self.__compare_num}_TRUE)",
            f"D={TRUE}",
            f"(CMP_{self.__compare_num}_END)"
        ] + POP_2_AND_PUSH_D
        self.__write_lines_with_separator(lines)
        

    def __write_compare_same_sign(self, comparison: str):
        lines = [
            f"(CMP_{self.__compare_num}_SAME_SIGN)",
            "@SP",
            "A=M-1",
            "D=M",
            "A=A-1",
            "D=M-D",
            f"@CMP_{self.__compare_num}_TRUE",
            f"D;J{comparison}",
            f"// Comparison {self.__compare_num} same sign false",
            f"@CMP_{self.__compare_num}_FALSE",
            "0;JMP"
        ]
        self.__write_lines_with_separator(lines)
    
    def __write_compare_different_sign(self, comparison: str):
        lines = [
            f"(CMP_{self.__compare_num}_Y_NEG_X_POS)",
            "// Here x >= 0 and y < 0, which means x > y,  therefore TRUE iff checking gt",
            f"@CMP_{self.__compare_num}_TRUE",
            f"{'0' if comparison == 'GT' else '1'};JEQ",
            f"@CMP_{self.__compare_num}_FALSE",
            "0;JMP",
            f"(CMP_{self.__compare_num}_Y_POS_X_NEG)",
            "// Here x < 0 and y >= 0, which means x < y,  therefore TRUE iff checking lt",
            f"@CMP_{self.__compare_num}_TRUE",
            f"{'0' if comparison == 'LT' else '1'};JEQ",
            f"@CMP_{self.__compare_num}_FALSE",
            "0;JMP",
            
        ]
        self.__write_lines_with_separator(lines)
        


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
            self.__write_pop_indexed(segment, index)
        else:
            self.__write_pop_unindexed(segment, index)

    def __write_pop_unindexed(self, segment: str, index: int):
        lines = [
            "// Unindexed pop",
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

    def __write_pop_indexed(self, segment: str, index: int):
        lines = [
            "// Indexed pop",
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
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
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
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
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
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass
    
    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        pass