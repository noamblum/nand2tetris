"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import xml.etree.ElementTree as ET
from JackTokenizer import JackTokenizer


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
        self.__output_stream = output_stream

    
    def __append_current_token(self, parent):
        elem = ET.SubElement(parent, self.__tokenizer.token_type())
        elem.text = self.__tokenizer.token_value()
        self.__tokenizer.advance()
        

    def compile_class(self) -> ET.ElementTree:
        """Compiles a complete class."""
        class_xml = ET.Element("class")

        # Rest of code here

        # print the xml

    def compile_class_var_dec(self) -> ET.ElementTree:
        """Compiles a static declaration or a field declaration."""
        class_var_dec = ET.Element("classVarDec")

        # static/field
        self.__append_current_token(class_var_dec)

        # type
        self.__append_current_token(class_var_dec)

        # varName
        self.__append_current_token(class_var_dec)

        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()

            if t_type == "symbol" and t_val == ";":
                break

            elif t_type == "symbol" and t_val == ",":
                self.__append_current_token(class_var_dec)

            self.__append_current_token(class_var_dec)

        
        # ;
        self.__append_current_token(class_var_dec)

        return class_var_dec

    def compile_subroutine(self) -> ET.ElementTree:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        subroutine_dec = ET.Element("subroutineDec")

        # constructor/method/function
        self.__append_current_token(subroutine_dec)

        # type
        self.__append_current_token(subroutine_dec)

        # name
        self.__append_current_token(subroutine_dec)

        # (
        self.__append_current_token(subroutine_dec)

        subroutine_dec.append(self.compile_parameter_list())

        # )
        self.__append_current_token(subroutine_dec)

        subroutine_dec.append(self.compile_subroutine_body())

        return subroutine_dec


    def compile_subroutine_body(self) -> ET.ElementTree:
        subroutine_dec = ET.Element("subroutineBody")

        # {
        self.__append_current_token(subroutine_dec)

        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()

            if t_type == "keyword" and t_val == "var":
                subroutine_dec.append(self.compile_var_dec())
            else:
                break
        
        subroutine_dec.append(self.compile_statements())

        # }
        self.__append_current_token(subroutine_dec)

        return subroutine_dec


    def compile_parameter_list(self) -> ET.ElementTree:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        parameter_list = ET.Element("parameterList")

        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()
            
            # Expression list end
            if t_type == "symbol" and t_val == ")":
                break

            # Expression list separator
            elif t_type == "symbol" and t_val == ",":
                self.__append_current_token(parameter_list)

            self.__append_current_token(parameter_list)

            self.__append_current_token(parameter_list)

        return parameter_list

    def compile_var_dec(self) -> ET.ElementTree:
        """Compiles a var declaration."""
        var_dec = ET.Element("varDec")

        # var
        self.__append_current_token(var_dec)

        # type
        self.__append_current_token(var_dec)


        # varName
        self.__append_current_token(var_dec)


        while self.__tokenizer.has_more_tokens():
            t_type, t_val = self.__tokenizer.token_type(), self.__tokenizer.token_value()

            if t_type == "symbol" and t_val == ";":
                break

            elif t_type == "symbol" and t_val == ",":
                self.__append_current_token(var_dec)

            # varName
            self.__append_current_token(var_dec)

        
        # ;
        self.__append_current_token(var_dec)

        return var_dec

    def compile_statements(self) -> ET.ElementTree:
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

    def compile_do(self) -> ET.ElementTree:
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
        

    def compile_let(self) -> ET.ElementTree:
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
            

    def compile_while(self) -> ET.ElementTree:
        """Compiles a while statement."""
        while_statement = ET.Element("ifStatement")

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

    def compile_return(self) -> ET.ElementTree:
        """Compiles a return statement."""
        return_statement = ET.Element("returnStatement")
        
        # return keyword
        self.__append_current_token(return_statement)

        if self.__tokenizer.token_type() != "symbol" or self.__tokenizer.token_value() != ";":
            return_statement.append(self.compile_expression())
        
        # ;
        self.__append_current_token(return_statement)

        return return_statement

    def compile_if(self) -> ET.ElementTree:
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
        if self.__tokenizer.token_type() == "keyword" or self.__tokenizer.token_value() == "else":
            # else keyword
            self.__append_current_token(if_statement)

            # {
            self.__append_current_token(if_statement)

            if_statement.append(self.compile_statements())

            # }
            self.__append_current_token(if_statement)
        
        return if_statement
        
        

    def compile_expression(self) -> ET.ElementTree:
        """Compiles an expression."""
        # Your code goes here!
        pass

    def compile_term(self) -> ET.ElementTree:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        pass

    def compile_expression_list(self) -> ET.ElementTree:
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
