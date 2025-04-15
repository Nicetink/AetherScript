import sys
import re
import os
import ast
import logging
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout,
                             QPushButton, QWidget, QFileDialog, QLabel, QStatusBar, QMenuBar,
                             QTreeView, QDockWidget, QMenu, QInputDialog, QMessageBox)
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QFileSystemModel, QIcon, QPixmap
from PyQt6.QtCore import Qt, QDir

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AetherHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, theme='dark'):
        super().__init__(parent)
        self.theme = theme
        self.update_highlighting_rules()

    def update_highlighting_rules(self):
        self.highlighting_rules = []
        colors = {
            'dark': {
                'keyword': '#569cd6',
                'string': '#ce9178',
                'number': '#b5cea8',
                'comment': '#6a9955',
                'background': '#161b22',
                'text': '#c9d1d9'
            },
            'light': {
                'keyword': '#0000ff',
                'string': '#a31515',
                'number': '#098658',
                'comment': '#008000',
                'background': '#ffffff',
                'text': '#24292e'
            }
        }
        current = colors[self.theme]

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(current['keyword']))
        keyword_format.setFontWeight(QFont.Weight.Bold)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor(current['string']))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor(current['number']))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(current['comment']))

        keywords = ['let', 'print', 'if', 'else', 'input']
        for word in keywords:
            pattern = rf'\b{word}\b'
            self.highlighting_rules.append((pattern, keyword_format))

        self.highlighting_rules.append((r'"[^"]*"', string_format))
        self.highlighting_rules.append((r'\b\d+\.?\d*\b', number_format))
        self.highlighting_rules.append((r'//.*$', comment_format))

    def highlightBlock(self, text):
        for pattern, format_ in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, format_)

class AetherScriptInterpreter:
    def __init__(self):
        self.variables = {}

    def evaluate_expression(self, expr):
        expr = expr.strip()
        if expr.isdigit() or (expr.replace('.', '').isdigit() and expr.count('.') <= 1):
            return float(expr) if '.' in expr else int(expr)
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        if expr in self.variables:
            return self.variables[expr]
        try:
            expr = expr.replace(' ', '')
            if '+' in expr:
                left, right = expr.split('+', 1)
                return self.evaluate_expression(left) + self.evaluate_expression(right)
            if '-' in expr:
                left, right = expr.split('-', 1)
                return self.evaluate_expression(left) - self.evaluate_expression(right)
            if '*' in expr:
                left, right = expr.split('*', 1)
                return self.evaluate_expression(left) * self.evaluate_expression(right)
            if '/' in expr:
                left, right = expr.split('/', 1)
                return self.evaluate_expression(left) / self.evaluate_expression(right)
            return ast.literal_eval(expr)
        except Exception as e:
            logger.error(f"Failed to evaluate expression: {expr}, error: {str(e)}")
            raise ValueError(f"Invalid expression: {expr}")

    def execute(self, code):
        output = []
        lines = code.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith('//'):
                i += 1
                continue

            if line.startswith('let '):
                match = re.match(r'let (\w+) = (.+);', line)
                if not match:
                    return [f"Error: Invalid variable declaration: {line}"]
                var_name, expr = match.groups()
                try:
                    value = self.evaluate_expression(expr)
                    self.variables[var_name] = value
                except Exception as e:
                    return [f"Error: {str(e)}"]
                i += 1
                continue

            if line.startswith('print('):
                match = re.match(r'print\((.+)\);', line)
                if not match:
                    return [f"Error: Invalid print statement: {line}"]
                expr = match.group(1)
                try:
                    value = self.evaluate_expression(expr)
                    output.append(str(value))
                except Exception as e:
                    return [f"Error: {str(e)}"]
                i += 1
                continue

            if line.startswith('input('):
                match = re.match(r'input\("([^"]*)"\);', line)
                if not match:
                    return [f"Error: Invalid input statement: {line}"]
                prompt = match.group(1)
                user_input = "42"
                output.append(f"{prompt}{user_input}")
                self.variables['input_result'] = user_input
                i += 1
                continue

            if line.startswith('if '):
                match = re.match(r'if (.+) \{', line)
                if not match:
                    return [f"Error: Invalid if statement: {line}"]
                condition = match.group(1)
                try:
                    cond_value = self.evaluate_expression(condition)
                except Exception as e:
                    return [f"Error: {str(e)}"]
                
                block_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip() == '}':
                    block_lines.append(lines[i])
                    i += 1
                if i >= len(lines):
                    return [f"Error: Unclosed if block"]
                i += 1

                else_block = []
                if i < len(lines) and lines[i].strip().startswith('else'):
                    i += 1
                    while i < len(lines) and not lines[i].strip() == '}':
                        else_block.append(lines[i])
                        i += 1
                    if i >= len(lines):
                        return [f"Error: Unclosed else block"]
                    i += 1

                if cond_value:
                    output.extend(self.execute('\n'.join(block_lines)))
                elif else_block:
                    output.extend(self.execute('\n'.join(else_block)))
                continue

            return [f"Error: Unknown statement: {line}"]
        return output

class AetherIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AetherScript IDE")
        self.theme = 'dark'
        self.font_size = 12
        self.interpreter = AetherScriptInterpreter()
        self.setWindowIcon(QIcon('img/icon.ico'))
        self.init_ui()
        self.apply_theme()
        logger.info("AetherScript IDE initialized")

    def init_ui(self):
        menubar = self.menuBar()
        view_menu = menubar.addMenu("View")
        toggle_theme_action = view_menu.addAction("Toggle Theme")
        toggle_theme_action.triggered.connect(self.toggle_theme)

        help_menu = menubar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.file_dock = QDockWidget("File Explorer", self)
        self.file_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.file_tree = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath())
        self.file_model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.Files | QDir.Filter.Dirs)
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(QDir.currentPath()))
        self.file_tree.setColumnWidth(0, 200)
        self.file_tree.hideColumn(1)
        self.file_tree.hideColumn(2)
        self.file_tree.hideColumn(3)
        self.file_tree.doubleClicked.connect(self.open_file_from_tree)
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.file_dock.setWidget(self.file_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_dock)

        editor_layout = QVBoxLayout()
        toolbar = QHBoxLayout()
        new_btn = QPushButton("New")
        open_btn = QPushButton("Open")
        save_btn = QPushButton("Save")
        run_btn = QPushButton("Run")
        new_btn.clicked.connect(self.new_file)
        open_btn.clicked.connect(self.open_file)
        save_btn.clicked.connect(self.save_file)
        run_btn.clicked.connect(self.run_code)
        toolbar.addWidget(new_btn)
        toolbar.addWidget(open_btn)
        toolbar.addWidget(save_btn)
        toolbar.addWidget(run_btn)
        editor_layout.addLayout(toolbar)

        self.editor = QTextEdit()
        self.editor.setFont(QFont('Courier New', self.font_size))
        self.highlighter = AetherHighlighter(self.editor.document(), self.theme)
        editor_layout.addWidget(self.editor)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFixedHeight(100)
        editor_layout.addWidget(QLabel("Output:"))
        editor_layout.addWidget(self.output)

        self.error = QTextEdit()
        self.error.setReadOnly(True)
        self.error.setFixedHeight(50)
        editor_layout.addWidget(QLabel("Errors:"))
        editor_layout.addWidget(self.error)

        main_layout.addLayout(editor_layout)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        self.current_file = None

    def show_about_dialog(self):
        about_text = (
            "<b>AetherScript IDE</b><br>"
            "Version: 1.0<br>"
            "A simple and modern IDE for AetherScript, a beginner-friendly programming language.<br>"
            "Features:<br>"
            "- Syntax highlighting for .aether files<br>"
            "- File explorer with create/rename/delete<br>"
            "- Zoom (Ctrl+Wheel, Ctrl+Plus/Minus)<br>"
            "- Dark and light themes<br>"
            "<br>Website: <a href='https://nicetink.github.io/AetherScript/'>AetherScript</a><br>"
            "GitHub: <a href='#'>https://github.com/Nicetink/AetherScript</a><br>"
            "© 2025 Nicet Software and Nicet ink & 4KEY. Licensed under NSPL 1.0"
        )
        msg = QMessageBox(self)
        msg.setWindowTitle("About AetherScript IDE")
        msg.setText(about_text)
        msg.setIconPixmap(QPixmap('img/icon.ico').scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #161b22;
                color: #c9d1d9;
            }
            QMessageBox QLabel {
                color: #c9d1d9;
            }
            QMessageBox QPushButton {
                background-color: #238636;
                color: #ffffff;
                border: none;
                padding: 5px 10px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2ea043;
            }
        """ if self.theme == 'dark' else """
            QMessageBox {
                background-color: #ffffff;
                color: #24292e;
            }
            QMessageBox QLabel {
                color: #24292e;
            }
            QMessageBox QPushButton {
                background-color: #2da44e;
                color: #ffffff;
                border: none;
                padding: 5px 10px;
            }
            QMessageBox QPushButton:hover {
                background-color: #2c974b;
            }
        """)
        logger.info("Opened About dialog")
        msg.exec()

    def show_context_menu(self, point):
        index = self.file_tree.indexAt(point)
        if not index.isValid():
            return
        path = self.file_model.filePath(index)
        menu = QMenu(self)
        new_file_action = menu.addAction("New File")
        new_folder_action = menu.addAction("New Folder")
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        action = menu.exec(self.file_tree.mapToGlobal(point))
        
        if action == new_file_action:
            name, ok = QInputDialog.getText(self, "New File", "File name:")
            if ok and name:
                if not name.endswith('.aether'):
                    name += '.aether'
                new_path = os.path.join(os.path.dirname(path), name)
                try:
                    with open(new_path, 'w') as f:
                        f.write('')
                    logger.info(f"Created file: {new_path}")
                    self.statusBar.showMessage(f"Created {name}")
                except Exception as e:
                    logger.error(f"Failed to create file: {new_path}, error: {str(e)}")
                    self.error.setText(f"Error creating file: {str(e)}")
        
        elif action == new_folder_action:
            name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
            if ok and name:
                new_path = os.path.join(os.path.dirname(path), name)
                try:
                    os.makedirs(new_path, exist_ok=True)
                    logger.info(f"Created folder: {new_path}")
                    self.statusBar.showMessage(f"Created {name}")
                except Exception as e:
                    logger.error(f"Failed to create folder: {new_path}, error: {str(e)}")
                    self.error.setText(f"Error creating folder: {str(e)}")
        
        elif action == rename_action:
            name, ok = QInputDialog.getText(self, "Rename", "New name:", text=os.path.basename(path))
            if ok and name:
                new_path = os.path.join(os.path.dirname(path), name)
                try:
                    os.rename(path, new_path)
                    logger.info(f"Renamed {path} to {new_path}")
                    self.statusBar.showMessage(f"Renamed to {name}")
                except Exception as e:
                    logger.error(f"Failed to rename {path} to {new_path}, error: {str(e)}")
                    self.error.setText(f"Error renaming: {str(e)}")
        
        elif action == delete_action:
            reply = QMessageBox.question(self, "Delete", f"Delete {os.path.basename(path)}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                        logger.info(f"Deleted file: {path}")
                    elif os.path.isdir(path):
                        os.rmdir(path)
                        logger.info(f"Deleted folder: {path}")
                    self.statusBar.showMessage(f"Deleted {os.path.basename(path)}")
                except Exception as e:
                    logger.error(f"Failed to delete {path}, error: {str(e)}")
                    self.error.setText(f"Error deleting: {str(e)}")

    def open_file_from_tree(self, index):
        path = self.file_model.filePath(index)
        if os.path.isfile(path):
            try:
                with open(path, 'r') as f:
                    self.editor.setText(f.read())
                self.current_file = path
                logger.info(f"Opened file: {path}")
                self.statusBar.showMessage(f"Opened {path}")
            except Exception as e:
                logger.error(f"Failed to open file: {path}, error: {str(e)}")
                self.error.setText(f"Error opening file: {str(e)}")

    def apply_theme(self):
        if self.theme == 'dark':
            stylesheet = """
                QMainWindow, QWidget {
                    background-color: #0d1117;
                    color: #c9d1d9;
                }
                QTextEdit, QTreeView {
                    background-color: #161b22;
                    color: #c9d1d9;
                    border: 1px solid #30363d;
                    font-family: 'Courier New';
                }
                QPushButton {
                    background-color: #238636;
                    color: #ffffff;
                    border: none;
                    padding: 5px 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2ea043;
                }
                QPushButton:pressed {
                    background-color: #1f6feb;
                }
                QLabel {
                    color: #c9d1d9;
                }
                QMenuBar, QDockWidget {
                    background-color: #161b22;
                    color: #c9d1d9;
                }
                QMenuBar::item, QDockWidget {
                    background-color: #161b22;
                    color: #c9d1d9;
                }
                QMenuBar::item:selected {
                    background-color: #30363d;
                }
                QMenu {
                    background-color: #161b22;
                    color: #c9d1d9;
                }
                QMenu::item:selected {
                    background-color: #30363d;
                }
            """
        else:
            stylesheet = """
                QMainWindow, QWidget {
                    background-color: #ffffff;
                    color: #24292e;
                }
                QTextEdit, QTreeView {
                    background-color: #f6f8fa;
                    color: #24292e;
                    border: 1px solid #d0d7de;
                    font-family: 'Courier New';
                }
                QPushButton {
                    background-color: #2da44e;
                    color: #ffffff;
                    border: none;
                    padding: 5px 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2c974b;
                }
                QPushButton:pressed {
                    background-color: #1f6feb;
                }
                QLabel {
                    color: #24292e;
                }
                QMenuBar, QDockWidget {
                    background-color: #f6f8fa;
                    color: #24292e;
                }
                QMenuBar::item, QDockWidget {
                    background-color: #f6f8fa;
                    color: #24292e;
                }
                QMenuBar::item:selected {
                    background-color: #d0d7de;
                }
                QMenu {
                    background-color: #f6f8fa;
                    color: #24292e;
                }
                QMenu::item:selected {
                    background-color: #d0d7de;
                }
            """
        self.setStyleSheet(stylesheet)
        self.highlighter.theme = self.theme
        self.highlighter.update_highlighting_rules()
        self.editor.setFont(QFont('Courier New', self.font_size))
        self.output.setFont(QFont('Courier New', self.font_size))
        self.error.setFont(QFont('Courier New', self.font_size))
        self.highlighter.rehighlight()
        logger.info(f"Applied {self.theme} theme")

    def toggle_theme(self):
        self.theme = 'light' if self.theme == 'dark' else 'dark'
        self.apply_theme()
        self.statusBar.showMessage(f"Switched to {self.theme} theme")

    def wheel_event(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0 and self.font_size < 24:
                self.font_size += 1
            elif delta < 0 and self.font_size > 8:
                self.font_size -= 1
            self.editor.setFont(QFont('Courier New', self.font_size))
            self.output.setFont(QFont('Courier New', self.font_size))
            self.error.setFont(QFont('Courier New', self.font_size))
            self.statusBar.showMessage(f"Font size: {self.font_size}px")
            logger.info(f"Font size changed to {self.font_size}px")
        else:
            super(QTextEdit, self.editor).wheelEvent(event)

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
                if self.font_size < 24:
                    self.font_size += 1
                    self.editor.setFont(QFont('Courier New', self.font_size))
                    self.output.setFont(QFont('Courier New', self.font_size))
                    self.error.setFont(QFont('Courier New', self.font_size))
                    self.statusBar.showMessage(f"Font size: {self.font_size}px")
                    logger.info(f"Font size increased to {self.font_size}px")
            elif event.key() == Qt.Key.Key_Minus:
                if self.font_size > 8:
                    self.font_size -= 1
                    self.editor.setFont(QFont('Courier New', self.font_size))
                    self.output.setFont(QFont('Courier New', self.font_size))
                    self.error.setFont(QFont('Courier New', self.font_size))
                    self.statusBar.showMessage(f"Font size: {self.font_size}px")
                    logger.info(f"Font size decreased to {self.font_size}px")
        super().keyPressEvent(event)

    def new_file(self):
        self.editor.clear()
        self.output.clear()
        self.error.clear()
        self.current_file = None
        self.statusBar.showMessage("New file created")
        logger.info("Created new file")

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "AetherScript Files (*.aether);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    self.editor.setText(f.read())
                self.current_file = file_name
                logger.info(f"Opened file: {file_name}")
                self.statusBar.showMessage(f"Opened {file_name}")
            except Exception as e:
                logger.error(f"Failed to open file: {file_name}, error: {str(e)}")
                self.error.setText(f"Error opening file: {str(e)}")

    def save_file(self):
        if not self.current_file:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "AetherScript Files (*.aether);;All Files (*)")
            if not file_name:
                return
            if not file_name.endswith('.aether'):
                file_name += '.aether'
            self.current_file = file_name
        try:
            with open(self.current_file, 'w') as f:
                f.write(self.editor.toPlainText())
            logger.info(f"Saved file: {self.current_file}")
            self.statusBar.showMessage(f"Saved {self.current_file}")
        except Exception as e:
            logger.error(f"Failed to save file: {self.current_file}, error: {str(e)}")
            self.error.setText(f"Error saving file: {str(e)}")

    def run_code(self):
        self.output.clear()
        self.error.clear()
        code = self.editor.toPlainText()
        try:
            result = self.interpreter.execute(code)
            for line in result:
                self.output.append(line)
            if not result:
                self.output.append("No output")
            logger.info("Code executed successfully")
            self.statusBar.showMessage("Code executed")
        except Exception as e:
            logger.error(f"Failed to execute code, error: {str(e)}")
            self.error.setText(f"Runtime error: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ide = AetherIDE()
    ide.resize(1000, 600)
    ide.show()
    logger.info("Application started")
    sys.exit(app.exec())
