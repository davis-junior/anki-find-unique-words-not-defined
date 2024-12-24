from aqt import mw
from bs4 import BeautifulSoup
import enchant
import nltk
from nltk.stem import WordNetLemmatizer

from word_utils import (
    clean_question_html,
    filter_word,
    get_base_word_from_ly_word,
    map_word,
    nltk_tag_to_wordnet_tag,
)


def find_unique_words_not_defined_set() -> set:
    enchant_dict = enchant.Dict("en_US")
    lemmatizer = WordNetLemmatizer()

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
        lemmatized_question_words = [
            lemmatizer.lemmatize(w, nltk_tag_to_wordnet_tag(nltk.pos_tag([w])[0][1]))
            for w in question_words
        ]

        if question_words and len(question_words) > 0:
            first_words_of_questions_set.add(question_words[0])
            all_unique_words = all_unique_words.union(lemmatized_question_words)

        #
        # parse answer
        #
        answer_html = card.answer()
        answer_html = answer_html[answer_html.find("<hr id=answer>") :]

        soup = BeautifulSoup(answer_html, features="html.parser")

        for s in soup.select("hr#answer"):
            s.extract()

        # remove code
        for s in soup.select("pre"):
            s.extract()

        answer_text = soup.get_text().strip()
        answer_words = answer_text.split()
        answer_words = [s.lower() for s in answer_words]
        answer_words = list(filter(filter_word, answer_words))
        answer_words = list(map(map_word, answer_words))
        answer_words = list(filter(filter_word, answer_words))
        answer_words = list(filter(enchant_dict.check, answer_words))
        answer_words = list(map(get_base_word_from_ly_word, answer_words))
        lemmatized_answer_words = [
            lemmatizer.lemmatize(w, nltk_tag_to_wordnet_tag(nltk.pos_tag([w])[0][1]))
            for w in answer_words
        ]

        if lemmatized_answer_words and len(lemmatized_answer_words) > 0:
            all_unique_words = all_unique_words.union(lemmatized_answer_words)

    # get result: all unique words not defined
    return all_unique_words.difference(first_words_of_questions_set)
