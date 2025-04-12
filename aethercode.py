import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Токены
@dataclass
class Token:
    type: str
    value: str
    line: int

# Лексер
class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.tokens = []
        self.keywords = {"let", "fn", "if", "else", "for", "in", "return", "struct", "print"}
        self.patterns = [
            (r"\s+", None),  # Пропуск пробелов
            (r"//.*", None),  # Комментарии
            (r"\d+\.\d+", "FLOAT"),
            (r"\d+", "INTEGER"),
            (r'"[^"]*"', "STRING"),
            (r"[a-zA-Z_][a-zA-Z0-9_]*", "IDENTIFIER"),
            (r"\{", "LBRACE"),
            (r"\}", "RBRACE"),
            (r"\(", "LPAREN"),
            (r"\)", "RPAREN"),
            (r"\[", "LBRACKET"),
            (r"\]", "RBRACKET"),
            (r",", "COMMA"),
            (r":", "COLON"),
            (r"=", "EQUALS"),
            (r";", "SEMICOLON"),
            (r"\+", "PLUS"),
            (r"-", "MINUS"),
            (r"\*", "MULTIPLY"),
            (r"/", "DIVIDE"),
            (r">", "GREATER"),
            (r"<", "LESS"),
            (r"\.", "DOT"),
            (r"or", "OR"),
        ]

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.code):
            match = None
            for pattern, token_type in self.patterns:
                regex = re.compile(pattern)
                match = regex.match(self.code, self.pos)
                if match:
                    value = match.group(0)
                    self.pos = match.end()
                    if token_type:
                        if token_type == "IDENTIFIER" and value in self.keywords:
                            token_type = value.upper()
                        self.tokens.append(Token(token_type, value, self.line))
                    break
            else:
                if self.code[self.pos] == "\n":
                    self.line += 1
                    self.pos += 1
                else:
                    raise SyntaxError(f"Unexpected character at line {self.line}: {self.code[self.pos]}")
        return self.tokens

# Узлы AST
@dataclass
class Node:
    pass

@dataclass
class Program(Node):
    statements: List[Node]

@dataclass
class LetStatement(Node):
    name: str
    value: Node

@dataclass
class FunctionDecl(Node):
    name: str
    params: List[tuple[str, str]]  # (name, type)
    body: List[Node]

@dataclass
class StructDecl(Node):
    name: str
    fields: List[tuple[str, str]]  # (name, type)

@dataclass
class PrintStatement(Node):
    value: Node

@dataclass
class BinaryOp(Node):
    left: Node
    op: str
    right: Node

@dataclass
class Identifier(Node):
    value: str

@dataclass
class Literal(Node):
    value: Any
    type: str

@dataclass
class StructLiteral(Node):
    name: str
    fields: Dict[str, Node]

@dataclass
class FieldAccess(Node):
    object: Node
    field: str

# Парсер
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type: str = None) -> Token:
        token = self.peek()
        if token is None:
            raise SyntaxError("Unexpected end of input")
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token.type}")
        self.pos += 1
        return token

    def parse(self) -> Program:
        statements = []
        while self.peek():
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self) -> Node:
        token = self.peek()
        if token.type == "LET":
            return self.parse_let()
        elif token.type == "FN":
            return self.parse_function()
        elif token.type == "STRUCT":
            return self.parse_struct()
        elif token.type == "PRINT":
            return self.parse_print()
        else:
            raise SyntaxError(f"Unexpected token: {token.type}")

    def parse_let(self) -> LetStatement:
        self.consume("LET")
        name = self.consume("IDENTIFIER").value
        self.consume("EQUALS")
        value = self.parse_expression()
        self.consume("SEMICOLON")
        return LetStatement(name, value)

    def parse_function(self) -> FunctionDecl:
        self.consume("FN")
        name = self.consume("IDENTIFIER").value
        self.consume("LPAREN")
        params = []
        if self.peek().type != "RPAREN":
            while True:
                param_name = self.consume("IDENTIFIER").value
                self.consume("COLON")
                param_type = self.consume("IDENTIFIER").value
                params.append((param_name, param_type))
                if self.peek().type != "COMMA":
                    break
                self.consume("COMMA")
        self.consume("RPAREN")
        self.consume("LBRACE")
        body = []
        while self.peek().type != "RBRACE":
            body.append(self.parse_statement())
        self.consume("RBRACE")
        return FunctionDecl(name, params, body)

    def parse_struct(self) -> StructDecl:
        self.consume("STRUCT")
        name = self.consume("IDENTIFIER").value
        self.consume("LBRACE")
        fields = []
        while self.peek().type != "RBRACE":
            field_name = self.consume("IDENTIFIER").value
            self.consume("COLON")
            field_type = self.consume("IDENTIFIER").value
            fields.append((field_name, field_type))
            if self.peek().type == "COMMA":
                self.consume("COMMA")
        self.consume("RBRACE")
        return StructDecl(name, fields)

    def parse_print(self) -> PrintStatement:
        self.consume("PRINT")
        self.consume("LPAREN")
        value = self.parse_expression()
        self.consume("RPAREN")
        self.consume("SEMICOLON")
        return PrintStatement(value)

    def parse_expression(self) -> Node:
        return self.parse_binary_op(0)

    def parse_binary_op(self, precedence: int) -> Node:
        left = self.parse_primary()
        while True:
            token = self.peek()
            if not token or token.type not in ("PLUS", "MINUS", "MULTIPLY", "DIVIDE"):
                break
            op_precedence = {"PLUS": 1, "MINUS": 1, "MULTIPLY": 2, "DIVIDE": 2}.get(token.type, 0)
            if op_precedence < precedence:
                break
            op = self.consume().type
            right = self.parse_binary_op(op_precedence + 1)
            left = BinaryOp(left, op, right)
        return left

    def parse_primary(self) -> Node:
        token = self.peek()
        if token.type == "INTEGER":
            value = int(self.consume().value)
            return Literal(value, "int")
        elif token.type == "FLOAT":
            value = float(self.consume().value)
            return Literal(value, "float")
        elif token.type == "STRING":
            value = self.consume().value[1:-1]
            return Literal(value, "string")
        elif token.type == "IDENTIFIER":
            ident = self.consume().value
            if self.peek().type == "LBRACE":
                return self.parse_struct_literal(ident)
            if self.peek().type == "DOT":
                self.consume("DOT")
                field = self.consume("IDENTIFIER").value
                return FieldAccess(Identifier(ident), field)
            return Identifier(ident)
        else:
            raise SyntaxError(f"Unexpected token in expression: {token.type}")

    def parse_struct_literal(self, name: str) -> StructLiteral:
        self.consume("LBRACE")
        fields = {}
        while self.peek().type != "RBRACE":
            field_name = self.consume("IDENTIFIER").value
            self.consume("COLON")
            field_value = self.parse_expression()
            fields[field_name] = field_value
            if self.peek().type == "COMMA":
                self.consume("COMMA")
        self.consume("RBRACE")
        return StructLiteral(name, fields)

# Интерпретатор
class Interpreter:
    def __init__(self):
        self.globals: Dict[str, Any] = {}
        self.structs: Dict[str, List[tuple[str, str]]] = {}

    def interpret(self, program: Program):
        for stmt in program.statements:
            self.execute(stmt)

    def execute(self, stmt: Node):
        if isinstance(stmt, LetStatement):
            value = self.evaluate(stmt.value)
            self.globals[stmt.name] = value
        elif isinstance(stmt, StructDecl):
            self.structs[stmt.name] = stmt.fields
        elif isinstance(stmt, PrintStatement):
            value = self.evaluate(stmt.value)
            print(value)
        else:
            raise NotImplementedError(f"Statement {type(stmt)} not implemented")

    def evaluate(self, expr: Node) -> Any:
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Identifier):
            return self.globals.get(expr.value, None)
        elif isinstance(expr, BinaryOp):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            if expr.op == "PLUS":
                return left + right
            elif expr.op == "MINUS":
                return left - right
            elif expr.op == "MULTIPLY":
                return left * right
            elif expr.op == "DIVIDE":
                return left / right
        elif isinstance(expr, StructLiteral):
            return {name: self.evaluate(value) for name, value in expr.fields.items()}
        elif isinstance(expr, FieldAccess):
            obj = self.evaluate(expr.object)
            return obj.get(expr.field, None)
        else:
            raise NotImplementedError(f"Expression {type(expr)} not implemented")

# Главная функция
def run_aether_code(code: str):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(program)

# Пример использования
if __name__ == "__main__":
    code = """
    struct User {
        name: string,
        age: int
    }

    let user = User { name: "Alice", age: 30 };
    print(user.name);
    print(user.age);
    let x = 5 + 3 * 2;
    print(x);
    """
    try:
        run_aether_code(code)
    except Exception as e:
        print(f"Error: {e}")