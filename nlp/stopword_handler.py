"""
stopword_handler.py
--------------------
STAGE 4 of the NLP pipeline.

Removes common "stop words" (the, is, and, of, ...) that don't help
identify what a sentence is about. This makes keyword extraction much
more meaningful in the next stage.
"""

from .nltk_setup import ensure_nltk_data

ensure_nltk_data()

try:
    from nltk.corpus import stopwords as nltk_stopwords
    STOPWORDS = set(nltk_stopwords.words("english"))
except Exception:
    # Small built-in fallback list so the app still works with no
    # internet access at demo time.
    STOPWORDS = {
        "a", "an", "the", "and", "or", "but", "if", "of", "to", "in",
        "on", "for", "with", "is", "are", "was", "were", "be", "been",
        "being", "this", "that", "these", "those", "it", "as", "by",
        "at", "from", "shall", "will", "may", "such", "any", "all",
        "not", "no", "so", "than", "then", "there", "their", "its",
    }

# A few extra words that are common in government documents but
# still add no keyword value.
EXTRA_STOPWORDS = {"shall", "hereby", "thereof", "aforesaid", "said"}
STOPWORDS = STOPWORDS.union(EXTRA_STOPWORDS)


def remove_stopwords(tokens):
    """
    Filter out stop-words from a list of tokens.

    Args:
        tokens (list[str]): cleaned, lowercase tokens

    Returns:
        list[str]: tokens with stop-words removed
    """
    return [t for t in tokens if t not in STOPWORDS]


if __name__ == "__main__":
    print(remove_stopwords(["farmers", "who", "meet", "the", "required", "conditions"]))
