import enchant
from nltk.corpus import wordnet


enchant_dict = enchant.Dict("en_US")


def nltk_tag_to_wordnet_tag(nltk_tag):
    if nltk_tag.startswith("J"):
        return wordnet.ADJ
    elif nltk_tag.startswith("V"):
        return wordnet.VERB
    elif nltk_tag.startswith("N"):
        return wordnet.NOUN
    elif nltk_tag.startswith("R"):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def clean_question_html(soup):
    for s in soup.select("style"):
        s.extract()
    for s in soup.select(".deck"):
        s.extract()
    for s in soup.select("br"):
        s.extract()
    for s in soup.select("pre"):
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
