"""
lemmatizer.py
-------------
STAGE 5 of the NLP pipeline.

Reduces each word to its base ("dictionary") form, e.g. "farmers" ->
"farmer", "applying" -> "applying"/"apply". This groups together
different forms of the same word so keyword counting is accurate.
"""

from .nltk_setup import ensure_nltk_data

ensure_nltk_data()

try:
    from nltk.stem import WordNetLemmatizer
    _lemmatizer = WordNetLemmatizer()
    _NLTK_OK = True
except Exception:
    _NLTK_OK = False

# Tiny fallback rule-based lemmatizer for common suffixes, used only
# if the WordNet data could not be downloaded.
_SUFFIX_RULES = [("ies", "y"), ("ing", ""), ("ed", ""), ("es", ""), ("s", "")]


def _rule_based_lemma(word):
    for suffix, replacement in _SUFFIX_RULES:
        if word.endswith(suffix) and len(word) - len(suffix) + len(replacement) > 2:
            return word[: -len(suffix)] + replacement
    return word


def lemmatize_tokens(tokens):
    """
    Lemmatize a list of tokens.

    Args:
        tokens (list[str]): cleaned tokens (stop-words already removed)

    Returns:
        list[str]: lemmatized tokens
    """
    if _NLTK_OK:
        try:
            return [_lemmatizer.lemmatize(t) for t in tokens]
        except Exception:
            pass
    return [_rule_based_lemma(t) for t in tokens]


if __name__ == "__main__":
    print(lemmatize_tokens(["farmers", "applying", "documents", "benefits"]))
