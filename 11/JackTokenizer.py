"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    KEYWORD_REGEX = r"class|constructor|function|method|field|static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return"
    SYMBOL_REGEX = r"[{}()\[\].,;+-/\*\&\|<>=~^#]"
    INTEGER_CONSTANT_REGEX = r"\d+"
    STRING_CONSTANT_REGEX = r"(?<=\").*?(?=\")"
    IDENTIFIER_REGEX = r"[a-zA-Z_][\w\d_]*"
    
    TOKEN_REGEX = f"({STRING_CONSTANT_REGEX})|({SYMBOL_REGEX})|({INTEGER_CONSTANT_REGEX})|({KEYWORD_REGEX})(?!\w)|({IDENTIFIER_REGEX})"
    GROUP_TO_TYPE_DICT = {4: "keyword", 2: "symbol", 3: "integerConstant", 1: 'stringConstant', 5: 'identifier'}
    
    COMMENT_REGEX = r"(/\*.*?\*/|//[^\r\n]*$)|(\".*?\")" # First capturing group is for comments, second for string literals
                                                         # This way, we can efficiently separate real comments from
                                                         # Comment indicators inside string literals


    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        def token_type_finder(t):
            for i, s in enumerate(t):
                if s:
                    return s, JackTokenizer.GROUP_TO_TYPE_DICT[i + 1]
            return 0, ''
        uncommented_input = self.__uncomment_input(input_stream)
        tokenizer = re.compile(JackTokenizer.TOKEN_REGEX, re.MULTILINE)
        self.__tokens: typing.List[typing.Tuple[str, str]] = [token_type_finder(tok) for tok in tokenizer.findall(uncommented_input)]
        self.__active_token_ind = 0
        self.__input_file_name = input_stream.name

    def __uncomment_input(self, input_stream: typing.TextIO):
        """Returns the input stream, read as a string without comments and with all whitepspaces turned to a single space

        Args:
            input_stream (typing.TextIO): The input file to be converted

        Returns:
            str: The standardized string, as specified
        """
        input_stirng = input_stream.read()

        comment_remover = re.compile(JackTokenizer.COMMENT_REGEX, re.DOTALL | re.MULTILINE)

        def replacer(match):
            """
            A helper function which replaces comments and does not touch whitespace
            """
            if match.group(1) is not None: # If matched a comment
                return ''
            else: # In this case, matched a string literal
                return match.group(2) # Return that string

        return comment_remover.sub(replacer, input_stirng)


    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        return self.__active_token_ind < len(self.__tokens)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.__active_token_ind += 1

    def tokenize_input(self, output_tokens_file=False) -> ET:
        tokens = ET.Element('tokens')
        while self.has_more_tokens():
            se = ET.SubElement(tokens, self.token_type())
            se.text = self.token_value()
            self.advance()
        if output_tokens_file:
            tokens_string = minidom.parseString(ET.tostring(tokens)).toprettyxml(indent='\t')
            with open(f"{self.__input_file_name.replace('.jack', '')}TTest.xml", "w") as f:
                tokens_lines = tokens_string.split('\n')
                f.writelines(l + '\n' for l in tokens_lines[1:])

        return tokens


    def __get_active_token(self):
        return self.__tokens[self.__active_token_ind]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "keyword", "symbol", "identifier", "integerConstant", "stringConstant"
        """
        return self.__get_active_token()[1]

    def token_value(self) -> str:
        """
        Returns:
            str: the value of the current token.
        """
        return self.__get_active_token()[0]

    def rewind(self, step: int):
        """Rewind some tokens. Accepts only positive numbers

        Args:
            step (int): how many tokens to go back
        """
        if step < 0:
            return
        self.__active_token_ind = max(0, self.__active_token_ind - step)


if __name__ == "__main__":
    file_to_tokenize = sys.argv[1]
    with open(file_to_tokenize) as f:
        jt = JackTokenizer(f)
        jt.tokenize_input(True)