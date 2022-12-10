"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


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
    INTEGER_CONSTANT_REGEX = r"\d"
    STRING_CONSTANT_REGEX = r"\".*\""
    IDENTIFIER_REGEX = r"[a-zA-Z_][\w\d_]*"
    SYMBOL_SET = {'[',']','{','}','(',')','.',',',';','+','-','/','*','&','|','<','>','=','~','^','#'}

    NON_SPACE_WHITESPACE_REGEX = r"[^\S ]+"
    COMMENT_REGEX = r"(/\*.*?\*/|//[^\r\n]*$)|(\".*?\")" # First capturing group is for comments, second for string literals
                                                         # This way, we can efficiently separate real comments from
                                                         # Comment indicators inside string literals


    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.__input = self.__standardize_input(input_stream)
        self.__token_scan_start = 0

        self.__keyword_matcher = re.compile(JackTokenizer.KEYWORD_REGEX)
        self.__symbol_matcher = re.compile(JackTokenizer.SYMBOL_REGEX)
        self.__int_const_matcher = re.compile(JackTokenizer.INTEGER_CONSTANT_REGEX)
        self.__str_const_matcher = re.compile(JackTokenizer.STRING_CONSTANT_REGEX)
        self.__identifier_matcher = re.compile(JackTokenizer.IDENTIFIER_REGEX)

        self.__active_token = ''
        self.__next_token = self.__find_next_token()

    def __standardize_input(self, input_stream: typing.TextIO):
        """Returns the input stream, read as a string without comments and with all whitepspaces turned to a single space

        Args:
            input_stream (typing.TextIO): The input file to be converted

        Returns:
            str: The standardized string, as specified
        """
        input_stirng = input_stream.read()

        comment_remover = re.compile(JackTokenizer.COMMENT_REGEX, re.DOTALL | re.MULTILINE)
        whitespace_matcher = re.compile(JackTokenizer.NON_SPACE_WHITESPACE_REGEX, re.MULTILINE)

        def replacer(match):
            """
            A helper function which replaces comments and does not touch whitespace
            """
            if match.group(1) is not None: # If matched a comment
                return ''
            else: # In this case, matched a string literal
                return match.group(1) # Return that string

        input_stirng = comment_remover.sub(replacer, input_stirng)

        return whitespace_matcher.sub('', input_stirng)


    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        return self.__next_token != ''

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.__active_token = self.__next_token
        self.__next_token = self.__find_next_token()

    def __find_next_token(self):
        next_token = ''
        chars_read = 0
        in_string_literal = False
        is_number = False
        for i in range(self.__token_scan_start, len(self.__input)):
            c = self.__input[i]
            chars_read += 1
            if next_token == '' and c == ' ':
                continue
            elif next_token == '' and c in JackTokenizer.SYMBOL_SET:
                next_token += c
                break
            elif next_token == '' and c == '"':
                in_string_literal = True
                continue
            elif in_string_literal and c == '"':
                break
            elif not in_string_literal and c == ' ':
                break
            elif not in_string_literal and c in JackTokenizer.SYMBOL_SET:
                chars_read -= 1
                break
            elif next_token != '' and c == '"':
                break
            elif next_token == '' and c.isdigit():
                is_number = True
                next_token += c
                continue
            elif not c.isdigit() and is_number:
                chars_read -= 1
                break
            else:
                next_token += c
        
        self.__token_scan_start += chars_read
        return next_token

    def get_active_token(self):
        return self.__active_token

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        pass

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        pass

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        # Your code goes here!
        pass

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        # Your code goes here!
        pass

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        # Your code goes here!
        pass

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        # Your code goes here!
        pass

if __name__ == "__main__":
    with open("SimpleTest/SimpleTest.jack") as f:
        jt = JackTokenizer(f)
        while jt.has_more_tokens():
            jt.advance()
            print(jt.get_active_token())