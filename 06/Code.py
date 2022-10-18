"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import re

JUMP_DICT = {
    "": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}


class Code:
    """Translates Hack assembly language mnemonics into binary codes."""
    
    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a dest mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        dst = ['0','0','0']
        if 'A' in mnemonic:
            dst[0] = '1'
        if 'D' in mnemonic:
            dst[1] = '1'
        if 'M' in mnemonic:
            dst[2] = '1'
        return ''.join(dst)

    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: the binary code of the given mnemonic.
        """
        a_bit = "1" if "M" in mnemonic else "0"
        comp = ""

        if mnemonic == "0": comp = "101010"
        elif mnemonic == "1": comp = "111111"
        elif mnemonic == "-1": comp = "111010"
        elif mnemonic == "D": comp = "001100"
        elif re.match(r"^[AM]$", mnemonic): comp = "110000"
        elif mnemonic == "!D": return "001101"
        elif re.match(r"^![AM]$", mnemonic): comp = "110001"
        elif mnemonic == "-D": comp = "001111"
        elif re.match(r"^-[AM]$", mnemonic): comp = "110011"
        elif mnemonic == "D+1": comp = "011111"
        elif re.match(r"^[AM]\+1$", mnemonic): comp = "110111"
        elif mnemonic == "D-1": comp = "001110"
        elif re.match(r"^[AM]-1$", mnemonic): comp = "110010"
        elif re.match(r"^([AM]\+D|D\+[AM])$", mnemonic): comp = "000010"
        elif re.match(r"^D-[AM]$", mnemonic): comp = "010011"
        elif re.match(r"^[AM]-D$", mnemonic): comp = "000111"
        elif re.match(r"^([AM]&D|D&[AM])$", mnemonic): comp = "000000"
        elif re.match(r"^([AM]\|D|D\|[AM])$", mnemonic): comp = "010101"
        elif re.match(r"^[AM]<<$", mnemonic): comp = "100000"
        elif mnemonic == "D<<": comp = "110000"
        elif re.match(r"^[AM]>>$", mnemonic): comp = "000000"
        elif mnemonic == "D>>": comp = "010000"

        return a_bit + comp


    @staticmethod
    def jump(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a jump mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        return JUMP_DICT[mnemonic]
