import SWA

###################################
#             TOKENS              #
###################################

# Constant for integers
Digits = '0123456789'

# Error class
class Error:
    def __init__(self, pos_start, pos_end, errorName, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.errorName = errorName
        self.details = details

    def as_string(self):
        result = f'{self.errorName}: {self.details}'
        result += f'\nFile: {self.pos_start.fn}, line {self.pos_start.ln}'
        result += '\n' + SWA(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

class IllCharacterError(Error):
    def __init__(self, pos_start, pos_end, char, details):
        super().__init__(pos_start, pos_end, f"Illegal character: '{char}'", details)

class IllSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, details)

# Position
class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, Current_Charcter=None):
        self.idx += 1
        self.col += 1

        if Current_Charcter == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

# Tokens for classes
IdT_Int = "int"
IdT_Str = "str"
IdT_Flt = "float"
IdT_Bool = "bool"

# Tokens for operations
IdT_Add = "ADDITION"
IdT_Subtract = "SUBTRACTION"
IdT_Multiply = "MULTIPLICATION"
IdT_Divide = "DIVISION"

# Tokens for parens "()"
IdT_LBracket = "Left_bracket"
IdT_RBracket = "Right_bracket"

# Other Tokens
IdT_EOF = "EOF"

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return self.type

##################################
#             LEXER              #
##################################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_character = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_character)
        self.current_character = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def create_tokens(self):
        tokens = []

        while self.current_character is not None:
            if self.current_character in ' \t':
                self.advance()
            elif self.current_character in Digits:
                tokens.append(self.create_integer())
            elif self.current_character == '+':
                tokens.append(Token(IdT_Add, pos_start=self.pos))
                self.advance()
            elif self.current_character == '-':
                tokens.append(Token(IdT_Subtract, pos_start=self.pos))
                self.advance()
            elif self.current_character == '*':
                tokens.append(Token(IdT_Multiply, pos_start=self.pos))
                self.advance()
            elif self.current_character == '/':
                tokens.append(Token(IdT_Divide, pos_start=self.pos))
                self.advance()
            elif self.current_character == '(':
                tokens.append(Token(IdT_LBracket, pos_start=self.pos))
                self.advance()
            elif self.current_character == ')':
                tokens.append(Token(IdT_RBracket, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                illegal_char = self.current_character
                self.advance()
                return [], IllCharacterError(pos_start, self.pos, illegal_char, "\n")

        tokens.append(Token(IdT_EOF, self.pos, self.pos))
        return tokens, None

    def create_integer(self):
        int_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_character is not None and self.current_character in Digits + '.':
            if self.current_character == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                int_str += '.'
            else:
                int_str += self.current_character
            self.advance()

        if dot_count == 0:
            return Token(IdT_Int, int(int_str), pos_start, self.pos)
        else:
            return Token(IdT_Flt, float(int_str), pos_start, self.pos)

# Defining nodes
class IntNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'

class BinaryOperationNode:
    def __init__(self, node1, operator_token, node2):
        self.node1 = node1
        self.operator_token = operator_token
        self.node2 = node2

    def __repr__(self):
        return f'({self.node1}, {self.operator_token}, {self.node2})'

# Parse result
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

# Parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_idx = -1  # Start from the first token
        self.advance()

    def advance(self):
        self.token_idx += 1
        if self.token_idx < len(self.tokens):
            self.current_token = self.tokens[self.token_idx]
        return self.current_token

    # ... (other methods)

    def parse(self):
        res = self.expression()
        if not res.error and self.current_token.type != IdT_EOF:
            return res.failure("Unexpected token: " + self.current_token)
        return res

    def factor(self):
        res = ParseResult()
        token = self.current_token

        if token.type in (IdT_Int, IdT_Flt):
            res.register(self.advance())  # Advance to the next token
            return res.success(IntNode())

        return res.failure(IllSyntaxError(token.pos_start, token.pos_end, "Expected int or float"))

    def term(self):
        return self.binary_operation(self.factor, (IdT_Divide, IdT_Multiply))

    def expression(self):
        return self.binary_operation(self.term, (IdT_Subtract, IdT_Add))

    def binary_operation(self, func, operation_tokens):
        res = ParseResult()
        node1 = res.register(func())
        if res.error:
            return res

        while self.current_token.type in operation_tokens:
            operator_token = self.current_token
            res.register(self.advance())
            node2 = res.register(func())
            if res.error:
                return res
            node1 = BinaryOperationNode(node1, operator_token, node2)

        return res.success(node1)

# Run file
def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.create_tokens()

    if error:
        return error

    parser = Parser(tokens)
    ast = parser.parse()

    return ast.node, ast.error

if __name__ == "__shell__":
    while True:
        in_text = input("Beer: ")
        result, error = run('<stdin>', in_text)

        if error:
            print(error.as_string())
        else:
            print(result)
