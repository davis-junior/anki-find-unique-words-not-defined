# AnkiFindUniqueWordsNotDefined
An Anki addon that scans all the words in your collection and checks if each word is defined.

## Description
A word is considered defined if the word is the first word in any question card in your collection. Output is shown in a QT text editor dialog after processing. The add-on is invoked through a drop down menu option that should show if the add-on is successfully installed.

## Install instructions
Create a new folder in your Anki add-ons folder. Place the __init__.py file inside. Also pip install pyenchant and ntlk. Copy from Python site-packages (either system or virtual environment depending on what you used to install the pip packages) folders enchant, ntlk, and regex into the Anki add-on folder.
