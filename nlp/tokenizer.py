"""
tokenizer.py
------------
STAGE 2 of the NLP pipeline.

Breaks each sentence down into individual words (tokens). Tokens are
what the later stages (cleaning, stop-word removal, lemmatization,
keyword extraction) actually operate on.
"""

import re
from .nltk_setup import ensure_nltk_data

ensure_nltk_data()

try:
    from nltk.tokenize import word_tokenize
    _NLTK_OK = True
except Exception:
    _NLTK_OK = False


def _regex_word_tokenize(sentence):
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+", sentence)


def tokenize(sentence):
    """
    Split a single sentence into a list of word tokens.

    Args:
        sentence (str): one sentence of text

    Returns:
        list[str]: word tokens
    """
    if not sentence:
        return []

    if _NLTK_OK:
        try:
            return word_tokenize(sentence)
        except Exception:
            return _regex_word_tokenize(sentence)
    return _regex_word_tokenize(sentence)


def tokenize_sentences(sentences):
    """Tokenize a list of sentences, returning a list of token lists."""
    return [tokenize(s) for s in sentences]


if __name__ == "__main__":
    print(tokenize("Farmers who meet the required conditions can apply."))
