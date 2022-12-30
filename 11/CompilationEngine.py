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
        self.__tokenizer.advance()

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
        
        self.__writer.write_function(subroutine_name, self.__symbol_table.var_count("var"))
        
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
        statements = ET.Element("statements")

        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()
            
            # Expression list end
            if t_type == "symbol" and t_val == "}":
                break

            elif t_type == "keyword" and t_val == "if":
                statements.append(self.compile_if())

            elif t_type == "keyword" and t_val == "while":
                statements.append(self.compile_while())

            elif t_type == "keyword" and t_val == "do":
                statements.append(self.compile_do())

            elif t_type == "keyword" and t_val == "let":
                statements.append(self.compile_let())

            elif t_type == "keyword" and t_val == "return":
                statements.append(self.compile_return())

        return statements

    def compile_do(self) -> None:
        """Compiles a do statement."""
        do_statement = ET.Element("doStatement")
        
        # do keyword
        self.__append_current_token(do_statement)

        # func/class name
        self.__append_current_token(do_statement)

        if self.__tokenizer.token_value() == ".":
            self.__append_current_token(do_statement)

            # func name
            self.__append_current_token(do_statement)

        # (
        self.__append_current_token(do_statement)

        do_statement.append(self.compile_expression_list())

        # )
        self.__append_current_token(do_statement)

        # ;
        self.__append_current_token(do_statement)

        return do_statement
        

    def compile_let(self) -> None:
        """Compiles a let statement."""
        let_statement = ET.Element("letStatement")

        # let keyword
        self.__append_current_token(let_statement)

        # var name
        self.__append_current_token(let_statement)

        if self.__tokenizer.token_value() == "[":
            self.__append_current_token(let_statement)

            let_statement.append(self.compile_expression())

            # ]
            self.__append_current_token(let_statement)

        # =
        self.__append_current_token(let_statement)

        let_statement.append(self.compile_expression())

        # ;
        self.__append_current_token(let_statement)

        return let_statement
            

    def compile_while(self) -> None:
        """Compiles a while statement."""
        while_statement = ET.Element("whileStatement")

        # while keyword
        self.__append_current_token(while_statement)

        # (
        self.__append_current_token(while_statement)

        while_statement.append(self.compile_expression())

        # )
        self.__append_current_token(while_statement)
        
        # {
        self.__append_current_token(while_statement)

        while_statement.append(self.compile_statements())

        # }
        self.__append_current_token(while_statement)
        
        return while_statement

    def compile_return(self) -> None:
        """Compiles a return statement."""
        return_statement = ET.Element("returnStatement")
        
        # return keyword
        self.__append_current_token(return_statement)

        if self.__tokenizer.token_type() != "symbol" or self.__tokenizer.token_value() != ";":
            return_statement.append(self.compile_expression())
        
        # ;
        self.__append_current_token(return_statement)

        return return_statement

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        if_statement = ET.Element("ifStatement")

        # if keyword
        self.__append_current_token(if_statement)

        # (
        self.__append_current_token(if_statement)

        if_statement.append(self.compile_expression())

        # )
        self.__append_current_token(if_statement)
        
        # {
        self.__append_current_token(if_statement)

        if_statement.append(self.compile_statements())

        # }
        self.__append_current_token(if_statement)
        
        # Optional else statement
        if self.__tokenizer.token_type() == "keyword" and self.__tokenizer.token_value() == "else":
            # else keyword
            self.__append_current_token(if_statement)

            # {
            self.__append_current_token(if_statement)

            if_statement.append(self.compile_statements())

            # }
            self.__append_current_token(if_statement)
        
        return if_statement
        
        

    def compile_expression(self) -> None:
        """Compiles an expression."""
        expression = ET.Element("expression")
        expression.append(self.compile_term())
        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()
            
            # Expression list end
            if t_type == "symbol" and t_val in {'+', '-', '*', '/', '&', '|', '<', '>', '='}:
                self.__append_current_token(expression)
                expression.append(self.compile_term())
            
            else:
                break
        
        return expression


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
        term = ET.Element("term")
        t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()

        if t_type in {'integerConstant', 'stringConstant'} or \
            (t_type == 'keyword' and t_val in {'true', 'false', 'null', 'this'}):
            self.__append_current_token(term)

        elif t_type == 'symbol' and t_val in {'-', '~', '^', '#'}:
            self.__append_current_token(term)
            term.append(self.compile_term())
        
        elif t_type == 'symbol' and t_val == '(':
            # (
            self.__append_current_token(term)
            term.append(self.compile_expression())
            # )
            self.__append_current_token(term)
        
        else:
            # varName/ start of subroutine call
            self.__append_current_token(term)

            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()

            if t_type == 'symbol' and t_val == '[':
                self.__append_current_token(term)
                term.append(self.compile_expression())
                self.__append_current_token(term)
            
            elif t_type == 'symbol' and t_val == '(':
                self.__append_current_token(term)
                term.append(self.compile_expression_list())
                self.__append_current_token(term)

            elif t_type == 'symbol' and t_val == '.':
                # .
                self.__append_current_token(term)

                # subroutineName
                self.__append_current_token(term)
                # (
                self.__append_current_token(term)
                term.append(self.compile_expression_list())
                # )
                self.__append_current_token(term)

        return term
        

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""

        expression_list = ET.Element("expressionList")

        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()
            
            # Expression list end
            if t_type == "symbol" and t_val == ")":
                break

            # Expression list separator
            elif t_type == "symbol" and t_val == ",":
                self.__append_current_token(expression_list)

            expression_list.append(self.compile_expression())

        return expression_list