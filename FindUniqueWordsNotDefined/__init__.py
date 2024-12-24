import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import nltk

from gui import add_main_menu_option


#
# main
#
nltk.download("wordnet", quiet=True)
nltk.download("averaged_perceptron_tagger_eng", quiet=True)

add_main_menu_option()
