"""
nltk_setup.py
-------------
Small helper that makes sure the NLTK data files we need (punkt for
sentence/word tokenizing, stopwords, wordnet for lemmatization) are
available. It tries to use them, and if they are missing it downloads
them once. This keeps every other NLP file simple and focused on one
job only.
"""

import nltk


REQUIRED_PACKAGES = [
    ("tokenizers/punkt", "punkt"),
    ("tokenizers/punkt_tab", "punkt_tab"),
    ("corpora/stopwords", "stopwords"),
    ("corpora/wordnet", "wordnet"),
    ("corpora/omw-1.4", "omw-1.4"),
]


def ensure_nltk_data():
    """Download any missing NLTK data files (only happens once)."""
    for path, package_name in REQUIRED_PACKAGES:
        try:
            nltk.data.find(path)
        except LookupError:
            try:
                nltk.download(package_name, quiet=True)
            except Exception:
                # If there is no internet access at demo time, the
                # individual pipeline files fall back to simple
                # regex-based behaviour instead of crashing.
                pass
