from anki.collection import Collection
from aqt import mw
from aqt.operations import QueryOp

from aqt.utils import qconnect
from aqt.qt import *
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QTextEdit, QFileDialog

from query import find_unique_words_not_defined_set


class TextEditor(QMainWindow):
    def __init__(self, parent_window, default_text):
        super().__init__(parent_window)

        self.setWindowTitle("Find Unique Words Not Defined")
        self.setGeometry(100, 100, 800, 600)

        self.text_edit = QTextEdit(self)
        self.text_edit.setText(default_text)
        self.setCentralWidget(self.text_edit)

        self.create_menu_bar()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("New", self.new_file)
        file_menu.addAction("Open", self.open_file)
        file_menu.addAction("Save", self.save_file)
        file_menu.addAction("Save As", self.save_as_file)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

    def new_file(self):
        self.text_edit.clear()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            with open(file_path, "r") as file:
                self.text_edit.setText(file.read())

    def save_file(self):
        if not hasattr(self, "file_path"):
            self.save_as_file()
        else:
            with open(self.file_path, "w") as file:
                file.write(self.text_edit.toPlainText())

    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.file_path = file_path
            self.save_file()


def background_operation(col: Collection):
    word_set = find_unique_words_not_defined_set()

    text = ""
    for word in word_set:
        text = text + word + "<br>"

    return text


def on_success(text: str):
    window = TextEditor(mw.window(), text)
    window.show()


def find_unique_action():
    op = QueryOp(
        parent=mw,
        op=background_operation,
        success=on_success,
    )

    op.with_progress().run_in_background()


def add_main_menu_option():
    action = QAction("Find Unique Words Not Defined", mw)
    qconnect(action.triggered, find_unique_action)
    mw.form.menuTools.addAction(action)
