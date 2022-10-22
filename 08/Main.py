"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing


from Parser import C_POP, C_PUSH, C_ARITHMETIC, C_LABEL, C_GOTO, C_IF, C_FUNCTION, C_RETURN, C_CALL
from Parser import Parser
from CodeWriter import CodeWriter


def translate_file(
        input_file: typing.TextIO, output_file: typing.TextIO,
        bootstrap: bool) -> None:
    """Translates a single file.

    Args:
        input_file (typing.TextIO): the file to translate.
        output_file (typing.TextIO): writes all output to this file.
        bootstrap (bool): if this is True, the current file is the 
            first file we are translating.
    """
    p = Parser(input_file)
    cw = CodeWriter(output_file)
    cw.set_file_name(os.path.splitext(os.path.basename(input_file.name))[0])

    if bootstrap:
        pass
        cw.write_bootstrap()

    while True:
        output_file.write(f"//{p.get_current_command()}\n")
        command_type = p.command_type()
        if command_type in (C_POP, C_PUSH):
            cw.write_push_pop(command_type, p.arg1(), p.arg2())
        elif command_type == C_ARITHMETIC:
            cw.write_arithmetic(p.arg1())
        elif command_type == C_LABEL:
            cw.write_label(p.arg1())
        elif command_type == C_GOTO:
            cw.write_goto(p.arg1())
        elif command_type == C_IF:
            cw.write_if(p.arg1())
        elif command_type == C_FUNCTION:
            cw.write_function(p.arg1(), p.arg2())
        elif command_type == C_RETURN:
            cw.write_return()
        elif command_type == C_CALL:
            cw.write_call(p.arg1(), p.arg2())

        if not p.has_more_commands(): break
        p.advance()


if "__main__" == __name__:
    # Parses the input path and calls translate_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: VMtranslator <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_translate = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
        output_path = os.path.join(argument_path, os.path.basename(
            argument_path))
    else:
        files_to_translate = [argument_path]
        output_path, extension = os.path.splitext(argument_path)
    output_path += ".asm"
    bootstrap = True
    with open(output_path, 'w') as output_file:
        for input_path in files_to_translate:
            filename, extension = os.path.splitext(input_path)
            if extension.lower() != ".vm":
                continue
            with open(input_path, 'r') as input_file:
                translate_file(input_file, output_file, bootstrap)
            bootstrap = False
