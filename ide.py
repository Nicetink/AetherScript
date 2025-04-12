import sys
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QFrame,
    QGraphicsDropShadowEffect,
    QFileDialog,
    QSplitter,
    QStyleFactory,
    QDockWidget,
)

# Интерпретатор AetherScript
@dataclass
class Token:
    type: str
    value: str
    line: int

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.tokens = []
        self.keywords = {"let", "fn", "struct", "print", "if", "else", "for", "in", "return"}
        self.patterns = [
            (r"\s+", None),
            (r"//.*", None),
            (r"\d+\.\d+", "FLOAT"),
            (r"\d+", "INTEGER"),
            (r'"[^"]*"', "STRING"),
            (r"[a-zA-Z_][a-zA-Z0-9_]*", "IDENTIFIER"),
            (r"\{", "LBRACE"),
            (r"\}", "RBRACE"),
            (r"\(", "LPAREN"),
            (r"\)", "RPAREN"),
            (r"=", "EQUALS"),
            (r";", "SEMICOLON"),
            (r"\+", "PLUS"),
            (r"-", "MINUS"),
            (r"\*", "MULTIPLY"),
            (r"/", "DIVIDE"),
            (r"\.", "DOT"),
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
                    raise SyntaxError(f"Unexpected character at line {self.line}")
        return self.tokens

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
            return Identifier(self.consume().value)
        else:
            raise SyntaxError(f"Unexpected token: {token.type}")

class Interpreter:
    def __init__(self, output_widget: QTextEdit):
        self.globals: Dict[str, Any] = {}
        self.output_widget = output_widget

    def interpret(self, program: Program):
        self.output_widget.clear()
        for stmt in program.statements:
            self.execute(stmt)

    def execute(self, stmt: Node):
        if isinstance(stmt, LetStatement):
            value = self.evaluate(stmt.value)
            self.globals[stmt.name] = value
        elif isinstance(stmt, PrintStatement):
            value = self.evaluate(stmt.value)
            self.output_widget.append(str(value))
        else:
            raise NotImplementedError(f"Statement {type(stmt)} not implemented")

    def evaluate(self, expr: Node) -> Any:
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Identifier):
            value = self.globals.get(expr.value)
            if value is None:
                raise NameError(f"Undefined variable: {expr.value}")
            return value
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
        else:
            raise NotImplementedError(f"Expression {type(expr)} not implemented")

def run_aether_script(code: str, output_widget: QTextEdit):
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        interpreter = Interpreter(output_widget)
        interpreter.interpret(program)
    except Exception as e:
        output_widget.clear()
        output_widget.append(f"Error: {str(e)}")

# Подсветка синтаксиса
class AetherHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = ["let", "fn", "struct", "print", "if", "else", "for", "in", "return"]
        for word in keywords:
            pattern = rf"\b{word}\b"
            self.highlighting_rules.append((pattern, keyword_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlighting_rules.append((r'"[^"]*"', string_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlighting_rules.append((r"\b\d+\b", number_format))
        self.highlighting_rules.append((r"\b\d+\.\d+\b", number_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlighting_rules.append((r"//.*", comment_format))

    def highlightBlock(self, text: str):
        for pattern, format in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format)

# Главное окно IDE
class AetherIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AetherScript IDE version 0.9.0")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)

        # Настройки стиля
        self.setStyleSheet("""
            QMainWindow {
                background: #1E1E2E;
            }
            QTextEdit {
                background: #2A2A3E;
                color: #D4D4D4;
                border: none;
                font-family: 'Consolas', monospace;
                font-size: 14px;
            }
            QPushButton {
                background: #3B3B5A;
                color: #D4D4D4;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #5B5B7A;
            }
            QPushButton:pressed {
                background: #2B2B4A;
            }
        """)

        # Главный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Панель инструментов
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet("background: #252535; border-radius: 8px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        toolbar.setGraphicsEffect(shadow)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 0, 10, 0)

        # Кнопки
        self.btn_new = self.create_button("📄 New", self.new_file)
        self.btn_open = self.create_button("📂 Open", self.open_file)
        self.btn_save = self.create_button("💾 Save", self.save_file)
        self.btn_run = self.create_button("▶ Run", self.run_code)

        toolbar_layout.addWidget(self.btn_new)
        toolbar_layout.addWidget(self.btn_open)
        toolbar_layout.addWidget(self.btn_save)
        toolbar_layout.addWidget(self.btn_run)
        toolbar_layout.addStretch()

        toolbar.setLayout(toolbar_layout)
        main_layout.addWidget(toolbar)

        # Основная область
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Боковая панель
        self.sidebar = QDockWidget("Files")
        self.sidebar.setStyleSheet("""
            QDockWidget {
                background: #252535;
                color: #D4D4D4;
                border-radius: 8px;
            }
            QDockWidget::title {
                background: #2A2A3E;
                padding: 10px;
                font-weight: bold;
            }
        """)
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_widget.setLayout(sidebar_layout)
        self.sidebar.setWidget(sidebar_widget)
        self.sidebar.setFixedWidth(0)  # Начально скрыта
        self.sidebar.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        # Кнопка для показа/скрытия боковой панели
        self.btn_toggle_sidebar = self.create_button("📋 Files", self.toggle_sidebar)
        toolbar_layout.addWidget(self.btn_toggle_sidebar)

        # Редактор кода
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 14))
        self.highlighter = AetherHighlighter(self.editor.document())

        # Вывод
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFixedHeight(150)
        self.output.setStyleSheet("border-top: 1px solid #3B3B5A;")

        # Разделение
        code_splitter = QSplitter(Qt.Orientation.Vertical)
        code_splitter.addWidget(self.editor)
        code_splitter.addWidget(self.output)
        code_splitter.setSizes([500, 150])

        splitter.addWidget(self.sidebar)
        splitter.addWidget(code_splitter)
        splitter.setSizes([0, 800])

        # Анимация боковой панели
        self.sidebar_anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_anim.setDuration(300)
        self.sidebar_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.sidebar_visible = False

        # Текущий файл
        self.current_file = None

    def create_button(self, text: str, callback):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(callback)

        # Анимация при наведении
        anim = QPropertyAnimation(btn, b"geometry")
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.Type.OutBack)

        def enter_event(e):
            anim.setStartValue(btn.geometry())
            anim.setEndValue(btn.geometry().adjusted(-2, -2, 2, 2))
            anim.start()

        def leave_event(e):
            anim.setStartValue(btn.geometry())
            anim.setEndValue(btn.geometry().adjusted(2, 2, -2, -2))
            anim.start()

        btn.enterEvent = enter_event
        btn.leaveEvent = leave_event
        return btn

    def toggle_sidebar(self):
        self.sidebar_visible = not self.sidebar_visible
        if self.sidebar_visible:
            self.sidebar_anim.setStartValue(0)
            self.sidebar_anim.setEndValue(200)
        else:
            self.sidebar_anim.setStartValue(200)
            self.sidebar_anim.setEndValue(0)
        self.sidebar_anim.start()

    def new_file(self):
        self.editor.clear()
        self.output.clear()
        self.current_file = None

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open AetherScript File", "", "AetherScript Files (*.aether);;All Files (*)"
        )
        if file_name:
            try:
                with open(file_name, "r", encoding="utf-8") as f:
                    self.editor.setText(f.read())
                self.current_file = file_name
            except Exception as e:
                self.output.setText(f"Error opening file: {str(e)}")

    def save_file(self):
        if not self.current_file:
            self.current_file, _ = QFileDialog.getSaveFileName(
                self, "Save AetherScript File", "", "AetherScript Files (*.aether);;All Files (*)"
            )
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
            except Exception as e:
                self.output.setText(f"Error saving file: {str(e)}")

    def run_code(self):
        code = self.editor.toPlainText()
        run_aether_script(code, self.output)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(30, 30, 46))
        gradient.setColorAt(1, QColor(20, 20, 36))
        painter.fillRect(self.rect(), gradient)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    ide = AetherIDE()
    ide.show()
    sys.exit(app.exec())