"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.__static_table = {}
        self.__field_table = {}
        self.__var_table = {}
        self.__arg_table = {}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.__var_table = {}
        self.__arg_table = {}

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind == "static":
            self.__static_table[name] = (type, len(self.__static_table))
        elif kind == "field":
            self.__field_table[name] = (type, len(self.__field_table))
        elif kind == "arg":
            self.__arg_table[name] = (type, len(self.__arg_table))
        elif kind == "var":
            self.__var_table[name] = (type, len(self.__var_table))

        

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        if kind == "static":
            return len(self.__static_table)
        elif kind == "field":
            return len(self.__field_table)
        elif kind == "arg":
            return len(self.__arg_table)
        elif kind == "var":
            return len(self.__var_table)

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name in self.__var_table:
            return "var"
        if name in self.__arg_table:
            return "arg"
        if name in self.__field_table:
            return "field"
        if name in self.__static_table:
            return "static"
        return None
        
    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.__var_table:
            return self.__var_table[name][0]

        if name in self.__arg_table:
            return self.__arg_table[name][0]

        if name in self.__field_table:
            return self.__field_table[name][0]

        if name in self.__static_table:
            return self.__static_table[name][0]
        return None

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.__var_table:
            return self.__var_table[name][1]
            
        if name in self.__arg_table:
            return self.__arg_table[name][1]

        if name in self.__field_table:
            return self.__field_table[name][1]

        if name in self.__static_table:
            return self.__static_table[name][1]
        
        return None
