"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re

COMMENT = '//'
A_COMMAND = "A_COMMAND"
L_COMMAND = "L_COMMAND"
C_COMMAND = "C_COMMAND"
A_PREFIX = '@'
L_PREFIX = '('
L_SUFFIX = ')'
DEST_INDICATOR = '='
JUMP_INDICATOR = ';'


class Parser:
    """Encapsulates access to the input code. Reads an assembly language 
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.__input_file = input_file
        self.__current_command = self.__find_next_command()
        self.__next_command = self.__find_next_command()

    def __find_next_command(self) -> str:
        next_line = self.__input_file.readline()
        whitespace = re.compile(r"\s+")
        while next_line != '':
            line_without_comments = next_line.split(COMMENT)[0]
            command = whitespace.sub("", line_without_comments)
            if command != '':
                return command
            next_line = self.__input_file.readline()
        return ''

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.__next_command != ''

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        if self.has_more_commands():
            self.__current_command = self.__next_command
            self.__next_command = self.__find_next_command()

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.__current_command.startswith(A_PREFIX): return A_COMMAND
        if self.__current_command.startswith(L_PREFIX): return L_COMMAND
        return C_COMMAND


    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        command_type = self.command_type()
        if command_type == A_COMMAND:
            return self.__current_command[1:]
        if command_type == L_COMMAND:
            return self.__current_command[1:-1]
        return ''

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == C_COMMAND:
            if DEST_INDICATOR not in self.__current_command: return ''
            return self.__current_command.split(DEST_INDICATOR)[0]
        return ''

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == C_COMMAND:
            dest_and_comp = self.__current_command.split(JUMP_INDICATOR)[0]
            if DEST_INDICATOR not in dest_and_comp: return dest_and_comp
            return dest_and_comp.split(DEST_INDICATOR)[1]
        return ''

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        if self.command_type() == C_COMMAND:
            if JUMP_INDICATOR not in self.__current_command: return ''
            return self.__current_command.split(JUMP_INDICATOR)[1]
        return ''
