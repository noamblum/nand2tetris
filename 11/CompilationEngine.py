"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

SEGMENT = {"arg": "argument", "static": "static", "field": "this", "var": "local"}

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, tokenizer: JackTokenizer, output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.__tokenizer = tokenizer
        self.__writer = VMWriter(output_stream)
        self.__symbol_table = SymbolTable()
        self.__class_name = ""
        self.__subroutine_name = ""
        self.__while_ind = 0
        self.__if_ind = 0
        
    def compile_class(self) -> None:
        """Compiles a complete class."""
        # class
        self.__tokenizer.advance()

        # className
        self.__class_name = self.__tokenizer.token_value()
        self.__tokenizer.advance()

        # {
        self.__tokenizer.advance()

        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()

            if t_type != 'keyword' or t_val not in {'static', 'field'}:
                break
            self.compile_class_var_dec()

        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()

            if t_type != 'keyword' or t_val not in {'constructor', 'function', 'method'}:
                break
            self.compile_subroutine()


        # }
        self.__tokenizer.advance()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # static/field
        kind = self.__tokenizer.token_value()
        self.__tokenizer.advance()

        # type
        type = self.__tokenizer.token_value()
        self.__tokenizer.advance()

        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()

            if t_type == 'identifier':
                name = t_val
                self.__symbol_table.define(name, type, kind)
                self.__tokenizer.advance()

            elif t_type == "symbol" and t_val == ";":
                break

            elif t_type == "symbol" and t_val == ",":
                self.__tokenizer.advance()
    
        # ;
        self.__tokenizer.advance()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # constructor/method/function
        self.__symbol_table.start_subroutine()
        subroutine_type = self.__tokenizer.token_value()
        self.__tokenizer.advance()
        
        # type
        self.__tokenizer.advance()

        # name
        subroutine_name = self.__tokenizer.token_value()
        self.__subroutine_name = subroutine_name
        self.__while_ind = 0
        self.__if_ind = 0
        self.__tokenizer.advance()

        if subroutine_type == "method":
            self.__symbol_table.define("this", self.__class_name ,"arg")

        # (
        self.__tokenizer.advance()

        self.compile_parameter_list(subroutine_type)

        # )
        self.__tokenizer.advance()

        self.compile_subroutine_body(subroutine_type, subroutine_name)


    def compile_subroutine_body(self, subroutine_type: str, subroutine_name: str) -> None:
        # {
        self.__tokenizer.advance()

        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()

            if t_type == "keyword" and t_val == "var":
                self.compile_var_dec()
            else:
                break
        
        self.__writer.write_function(f"{self.__class_name}.{subroutine_name}", self.__symbol_table.var_count("var"))

        if subroutine_type == "constructor":
            self.__writer.write_push("constant", self.__symbol_table.var_count("field"))
            self.__writer.write_call("Memory.alloc", 1)
            self.__writer.write_pop("pointer", 0)
        
        elif subroutine_type == "method":
            self.__writer.write_push("argument", 0)
            self.__writer.write_pop("pointer", 0)
        
        self.compile_statements()

        # }
        self.__tokenizer.advance()


    def compile_parameter_list(self, subroutine_type: str) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        if subroutine_type == "method":
            self.__symbol_table.define("this", "arg", self.__class_name)
        kind = "arg"
        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()
            
            # Expression list end
            if t_type == "symbol" and t_val == ")":
                break

            # Expression list separator
            elif t_type == "symbol" and t_val == ",":
                self.__tokenizer.advance()

            # type
            type = self.__tokenizer.token_value()
            self.__tokenizer.advance()

            # name
            name = self.__tokenizer.token_value()
            self.__tokenizer.advance()
            self.__symbol_table.define(name, type, kind)


    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # var
        kind = self.__tokenizer.token_value()
        self.__tokenizer.advance()

        # type
        type = self.__tokenizer.token_value()
        self.__tokenizer.advance()


        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()

            if t_type == 'identifier':
                name = t_val
                self.__symbol_table.define(name, type, kind)
                self.__tokenizer.advance()

            elif t_type == "symbol" and t_val == ";":
                break

            elif t_type == "symbol" and t_val == ",":
                self.__tokenizer.advance()
        
        # ;
        self.__tokenizer.advance()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()
            
            # Expression list end
            if t_type == "symbol" and t_val == "}":
                break

            elif t_type == "keyword" and t_val == "if":
                self.compile_if()

            elif t_type == "keyword" and t_val == "while":
                self.compile_while()

            elif t_type == "keyword" and t_val == "do":
                self.compile_do()

            elif t_type == "keyword" and t_val == "let":
                self.compile_let()

            elif t_type == "keyword" and t_val == "return":
                self.compile_return()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # do keyword
        self.__tokenizer.advance()

        self.compile_subroutine_call()

        # Do statements are void functions or we ignore their return value, so need to pop that placeholder returned value
        self.__writer.write_pop("temp", 0)

        # ;
        self.__tokenizer.advance()

    
    def compile_subroutine_call(self):
        # func/class name
        var_or_class_name = None
        func_name = self.__tokenizer.token_value()
        self.__tokenizer.advance()

        if self.__tokenizer.token_value() == ".":
            var_or_class_name = func_name
            
            # .
            self.__tokenizer.advance()

            # func name
            func_name = self.__tokenizer.token_value()
            self.__tokenizer.advance()

        # (
        self.__tokenizer.advance()

        n_args = 0
        if var_or_class_name is None:
            # this is a method of the curent object, push this
            func_name = f"{self.__class_name}.{func_name}"
            self.__writer.write_push("pointer", 0)
            n_args += 1
        
        elif self.__symbol_table.kind_of(var_or_class_name) is not None:
            kind = self.__symbol_table.kind_of(var_or_class_name)
            # This is a method of an object
            func_name = f"{self.__symbol_table.type_of(var_or_class_name)}.{func_name}"
            self.__writer.write_push(SEGMENT[kind], self.__symbol_table.index_of(var_or_class_name))
            n_args += 1
        else:
            # Otherwise this is a static function of a class, no need to push a first argument
            func_name = f"{var_or_class_name}.{func_name}"
        
        n_args += self.compile_expression_list()

        self.__writer.write_call(func_name, n_args)

        # )
        self.__tokenizer.advance()
        

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # let keyword
        self.__tokenizer.advance()

        # var name
        var_name = self.__tokenizer.token_value()
        self.__tokenizer.advance()

        if self.__tokenizer.token_value() == "[":
            # [
            self.__tokenizer.advance()

            
            self.__writer.write_push(SEGMENT[self.__symbol_table.kind_of(var_name)], self.__symbol_table.index_of(var_name))

            # Put the required index on top of the stack
            self.compile_expression()

            self.__writer.write_arithmetic("add")

            # ]
            self.__tokenizer.advance()

            # =
            self.__tokenizer.advance()

            self.compile_expression()

            self.__writer.write_pop("temp", 0)
            self.__writer.write_pop("pointer", 1)
            self.__writer.write_push("temp", 0)
            self.__writer.write_pop("that", 0)

        else:
            # =
            self.__tokenizer.advance()

            self.compile_expression()

            self.__writer.write_pop(SEGMENT[self.__symbol_table.kind_of(var_name)], self.__symbol_table.index_of(var_name))
        # ;
        self.__tokenizer.advance()
            

    def compile_while(self) -> None:
        """Compiles a while statement."""

        # while keyword
        self.__tokenizer.advance()

        # (
        self.__tokenizer.advance()

        loop_start_label = f"{self.__class_name}.{self.__subroutine_name}$WhileStart{self.__while_ind}"
        loop_end_label = f"{self.__class_name}.{self.__subroutine_name}$WhileEnd{self.__while_ind}"
        self.__while_ind += 1

        self.__writer.write_label(loop_start_label)

        self.compile_expression()

        self.__writer.write_arithmetic("not")

        self.__writer.write_if(loop_end_label)

        # )
        self.__tokenizer.advance()
        
        # {
        self.__tokenizer.advance()

        self.compile_statements()

        # }
        self.__tokenizer.advance()

        self.__writer.write_goto(loop_start_label)
        self.__writer.write_label(loop_end_label)

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # return keyword
        self.__tokenizer.advance()

        if self.__tokenizer.token_type() != "symbol" or self.__tokenizer.token_value() != ";":
            self.compile_expression()
        else:
            # Placeholder 0
            self.__writer.write_push("constant", 0)
        
        self.__writer.write_return()
        # ;
        self.__tokenizer.advance()


    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # if keyword
        self.__tokenizer.advance()

        # (
        self.__tokenizer.advance()

        self.compile_expression()
        self.__writer.write_arithmetic("not")

        # )
        self.__tokenizer.advance()
        
        # {
        self.__tokenizer.advance()

        else_label = f"{self.__class_name}.{self.__subroutine_name}$Else{self.__if_ind}"
        if_end_label = f"{self.__class_name}.{self.__subroutine_name}$IfEnd{self.__if_ind}"
        self.__if_ind += 1

        self.__writer.write_if(else_label)

        self.compile_statements()

        self.__writer.write_goto(if_end_label)

        # }
        self.__tokenizer.advance()

        self.__writer.write_label(else_label)
        # Optional else statement
        if self.__tokenizer.token_type() == "keyword" and self.__tokenizer.token_value() == "else":
            # else keyword
            self.__tokenizer.advance()

            # {
            self.__tokenizer.advance()

            self.compile_statements()

            # }
            self.__tokenizer.advance()
        
        self.__writer.write_label(if_end_label)
        
        

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()
            
            # Expression list end
            if t_type == "symbol" and t_val in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:

                operator = t_val

                self.__tokenizer.advance()

                self.compile_term()

                if operator == '+':
                    self.__writer.write_arithmetic("add")
                elif operator == '-':
                    self.__writer.write_arithmetic("sub")
                elif operator == '*':
                    self.__writer.write_call("Math.multiply", 2)
                elif operator == '/':
                    self.__writer.write_call("Math.divide", 2)
                elif operator == '&':
                    self.__writer.write_arithmetic("and")
                elif operator == '|':
                    self.__writer.write_arithmetic("or")
                elif operator == '<':
                    self.__writer.write_arithmetic("lt")
                elif operator == '>':
                    self.__writer.write_arithmetic("gt")
                elif operator == '=':
                    self.__writer.write_arithmetic("eq")
            
            else:
                break


    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()

        if t_type in {'integerConstant', 'stringConstant'} or \
            (t_type == 'keyword' and t_val in {'true', 'false', 'null', 'this'}):
            if t_type == 'integerConstant':
                self.__writer.write_push("constant", int(t_val))
            if t_type == 'stringConstant':
                self.__writer.write_push("constant", len(t_val))
                self.__writer.write_call("String.new", 1)
                for char in t_val:
                    self.__writer.write_push("constant", ord(char))
                    self.__writer.write_call("String.appendChar", 2)
            elif t_val == "true":
                self.__writer.write_push("constant", 1)
                self.__writer.write_arithmetic("neg")
            elif t_val in {"false", "null"}:
                self.__writer.write_push("constant", 0)
            elif t_val == "this":
                self.__writer.write_push("pointer", 0)
            self.__tokenizer.advance()

        elif t_type == 'symbol' and t_val in {'-', '~', '^', '#'}:
            operator = t_val
            self.__tokenizer.advance()
            self.compile_term()
            if operator == '-':
                self.__writer.write_arithmetic('neg')
            elif operator == '~':
                self.__writer.write_arithmetic('not')
            elif operator == '^':
                self.__writer.write_arithmetic('shiftleft')
            elif operator == '#':
                self.__writer.write_arithmetic('shiftright')
        
        elif t_type == 'symbol' and t_val == '(':
            # (
            self.__tokenizer.advance()
            self.compile_expression()
            # )
            self.__tokenizer.advance()
        
        else:
            # varName/ start of subroutine call
            var_name = self.__tokenizer.token_value()
            self.__tokenizer.advance()

            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()

            if t_type == 'symbol' and t_val == '[':
                # [
                self.__tokenizer.advance()
                self.__writer.write_push(SEGMENT[self.__symbol_table.kind_of(var_name)],
                                            self.__symbol_table.index_of(var_name))
                self.compile_expression()
                self.__writer.write_arithmetic("add")
                self.__writer.write_pop("pointer", 1)
                self.__writer.write_push("that", 0)
                # ]
                self.__tokenizer.advance()
            
            elif t_type == 'symbol' and t_val in {'(', '.'} :
                self.__tokenizer.rewind(1)
                self.compile_subroutine_call()
            else:
                self.__writer.write_push(SEGMENT[self.__symbol_table.kind_of(var_name)],
                                            self.__symbol_table.index_of(var_name))
        

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions. Returns that amount of expressions in the list"""

        n_expressions = 0
        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()
            
            # Expression list end
            if t_type == "symbol" and t_val == ")":
                break

            # Expression list separator
            elif t_type == "symbol" and t_val == ",":
                self.__tokenizer.advance()

            self.compile_expression()
            n_expressions += 1

        return n_expressions
