# pip install aqt PyQt6 beautifulsoup4

import os
import sys

sys.path.append(os.path.dirname(__file__))

from aqt import mw
from anki.collection import Collection
from aqt.operations import QueryOp
from aqt.utils import qconnect
from aqt.qt import *
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QTextEdit, QFileDialog
from bs4 import BeautifulSoup
import enchant
import nltk
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer


def nltk_tag_to_wordnet_tag(nltk_tag):
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:          
        return wordnet.NOUN


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
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
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
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")
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


def clean_question_html(soup):
    for s in soup.select('style'):
        s.extract()
    for s in soup.select('.deck'):
        s.extract()
    for s in soup.select('br'):
        s.extract()
    for s in soup.select('pre'):
        s.extract()


def filter_word(word: str):
    if not word or not word.strip():
        return False

    word = word.strip()

    if len(word) <= 1:
        return False

    if (
        ":" in word
        or "/" in word 
        or "\\" in word 
        or "'" in word
        or '"' in word 
        or "$" in word 
        or "@" in word
        or "%" in word
        or "^" in word
        or "+" in word
        or "=" in word
        or "|" in word
        or "_" in word
        or "*" in word
        or "#" in word
        or "¬" in word
        or "<" in word
        or ">" in word
        or "{" in word
        or "}" in word
        or "[" in word
        or "]" in word
        or "()" in word 
        or "(...)" in word
    ):
        return False
    
    if "." in word and "(" in word:
        return False

    if "." in word and ")" in word:
        return False

    if word.startswith("-") or word.endswith("-"):
        return False

    if "." in word and not (word.startswith(".") or word.endswith(".")):
        return False

    if "(" in word and not (word.startswith("(") or word.endswith("(")):
        return False

    if ")" in word and not (word.startswith(")") or word.endswith(")")):
        return False

    if ");" in word:
        return False

    if word.isnumeric():
        return False

    if not any([c.isalpha() for c in word]):
        return False

    return True


def map_word(word: str):
    word = word.strip()
    word = word.strip(",")
    word = word.strip(".")
    word = word.strip(";")
    word = word.strip("?")
    word = word.strip("!")
    word = word.strip(")")
    word = word.strip("(")
    word = word.strip("{")
    word = word.strip("}")
    word = word.strip("[")
    word = word.strip("]")
    word = word.strip("“")
    word = word.strip("”")
    word = word.strip("’")

    return word


def get_base_word_from_ly_word(word: str) -> str:
    if word.endswith("ally"):
        base_word = word[:-4]
        if base_word and enchant_dict.check(base_word):
            return base_word

    elif word.endswith("ily"):
        base_word = word[:-3] + "y"
        if base_word and enchant_dict.check(base_word):
            return base_word

    elif word.endswith("bly"):
        base_word = word[:-3] + "ble"
        if base_word and enchant_dict.check(base_word):
            return base_word

    elif word.endswith("ly"):
        base_word = word[:-2]
        if base_word and enchant_dict.check(base_word):
            return base_word
    
    return word


def find_unique_words_not_defined_set() -> set:
    first_words_of_questions_set = set()
    all_unique_words = set()

    ids = mw.col.find_cards("")

    for id in ids:
        card = mw.col.get_card(id)
    
        #
        # parse question
        #
        question_html = card.question()
        soup = BeautifulSoup(question_html, features="html.parser")
        clean_question_html(soup)
        question_text = soup.get_text().strip()
        question_words = question_text.split()
        question_words = [s.lower() for s in question_words]
        question_words = list(filter(filter_word, question_words))
        question_words = list(map(map_word, question_words))
        question_words = list(filter(filter_word, question_words))
        question_words = list(filter(enchant_dict.check, question_words))
        question_words = list(map(get_base_word_from_ly_word, question_words))
        lemmatized_question_words = [lemmatizer.lemmatize(w, nltk_tag_to_wordnet_tag(nltk.pos_tag([w])[0][1])) for w in question_words]


        if question_words and len(question_words) > 0:
            first_words_of_questions_set.add(question_words[0])
            all_unique_words = all_unique_words.union(lemmatized_question_words)

        #
        # parse answer
        #
        answer_html = card.answer()
        answer_html = answer_html[answer_html.find("<hr id=answer>"):]

        soup = BeautifulSoup(answer_html, features="html.parser")
 
        for s in soup.select('hr#answer'):
            s.extract()

        # remove code
        for s in soup.select('pre'):
            s.extract()

        answer_text = soup.get_text().strip()
        answer_words = answer_text.split()
        answer_words = [s.lower() for s in answer_words]
        answer_words = list(filter(filter_word, answer_words))
        answer_words = list(map(map_word, answer_words))
        answer_words = list(filter(filter_word, answer_words))
        answer_words = list(filter(enchant_dict.check, answer_words))
        answer_words = list(map(get_base_word_from_ly_word, answer_words))
        lemmatized_answer_words = [lemmatizer.lemmatize(w, nltk_tag_to_wordnet_tag(nltk.pos_tag([w])[0][1])) for w in answer_words]

        if lemmatized_answer_words and len(lemmatized_answer_words) > 0:
            all_unique_words = all_unique_words.union(lemmatized_answer_words)

    # get result: all unique words not defined
    return all_unique_words.difference(first_words_of_questions_set)


# main
enchant_dict = enchant.Dict("en_US")

nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)

lemmatizer = WordNetLemmatizer()
# w = "medicinally"
# print(w)
# print(nltk.pos_tag([w]))
# print(nltk_tag_to_wordnet_tag(nltk.pos_tag([w])[0][1]))
# print(lemmatizer.lemmatize(w, nltk_tag_to_wordnet_tag(nltk.pos_tag([w])[0][1])))

action = QAction("Find Unique Words Not Defined", mw)
qconnect(action.triggered, find_unique_action)
mw.form.menuTools.addAction(action)
