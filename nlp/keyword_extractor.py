"""
keyword_extractor.py
---------------------
STAGE 6 (final stage) of the NLP pipeline.

Uses simple word-frequency counting on the cleaned + lemmatized
tokens to find the most important words in the policy document. This
keeps the algorithm easy to explain in a presentation: "we count how
often each meaningful word appears, and the top ones are the
keywords."
"""

from collections import Counter

from .tokenizer import tokenize
from .text_cleaner import clean_tokens
from .stopword_handler import remove_stopwords
from .lemmatizer import lemmatize_tokens


def extract_keywords(text, top_n=12):
    """
    Run the full clean -> stopword-removal -> lemmatize -> count
    pipeline over a block of text and return the most frequent words.

    Args:
        text (str): full policy text (or a section of it)
        top_n (int): how many keywords to return

    Returns:
        list[tuple[str, int]]: (keyword, frequency) pairs, most frequent first
    """
    tokens = tokenize(text)
    tokens = clean_tokens(tokens)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize_tokens(tokens)

    if not tokens:
        return []

    counts = Counter(tokens)
    return counts.most_common(top_n)


def process_sentence(sentence):
    """
    Run one sentence through every pipeline stage and return the
    intermediate results — handy for showing "NLP processing" step by
    step during the demo.
    """
    raw_tokens = tokenize(sentence)
    cleaned = clean_tokens(raw_tokens)
    no_stopwords = remove_stopwords(cleaned)
    lemmas = lemmatize_tokens(no_stopwords)
    return {
        "sentence": sentence,
        "tokens": raw_tokens,
        "cleaned_tokens": cleaned,
        "without_stopwords": no_stopwords,
        "lemmas": lemmas,
    }


if __name__ == "__main__":
    sample = ("Eligible beneficiaries shall be entitled to financial "
              "assistance subject to fulfillment of prescribed "
              "eligibility criteria.")
    print(extract_keywords(sample))
