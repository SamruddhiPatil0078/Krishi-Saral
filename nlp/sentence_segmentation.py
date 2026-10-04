"""
sentence_segmentation.py
-------------------------
STAGE 1 of the NLP pipeline.

Splits a big block of policy text into individual sentences. This is
the first step because every later stage (tokenizing, keyword
classification, simplification) works one sentence at a time.
"""

import re
from .nltk_setup import ensure_nltk_data

ensure_nltk_data()

try:
    from nltk.tokenize import sent_tokenize
    _NLTK_OK = True
except Exception:
    _NLTK_OK = False


def _regex_sentence_split(text):
    """Fallback splitter used only if NLTK data isn't available."""
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text)
    return [p.strip() for p in parts if p.strip()]


def segment_sentences(text):
    """
    Turn raw policy text into a clean list of sentences.

    Args:
        text (str): raw text extracted from the PDF or pasted by the user

    Returns:
        list[str]: one entry per sentence
    """
    if not text or not text.strip():
        return []

    # Normalise line breaks that PDFs often introduce mid-sentence
    cleaned = re.sub(r"\n+", " ", text)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

    if _NLTK_OK:
        try:
            sentences = sent_tokenize(cleaned)
        except Exception:
            sentences = _regex_sentence_split(cleaned)
    else:
        sentences = _regex_sentence_split(cleaned)

    # Drop very short/noise fragments (page numbers, bullet symbols, etc.)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 8]
    return sentences


if __name__ == "__main__":
    sample = ("Eligible beneficiaries shall be entitled to financial "
              "assistance. The scheme is applicable to small and "
              "marginal farmers only.")
    for i, s in enumerate(segment_sentences(sample), 1):
        print(i, s)
