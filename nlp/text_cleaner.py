"""
text_cleaner.py
----------------
STAGE 3 of the NLP pipeline.

Cleans word tokens before they are analysed further: lowercases them,
strips punctuation/special characters, and removes pure-number tokens
that don't carry keyword meaning (dates are handled separately by the
policy_analyzer).
"""

import re


def clean_tokens(tokens):
    """
    Clean a list of raw tokens.

    Args:
        tokens (list[str]): tokens straight from the tokenizer

    Returns:
        list[str]: lowercase, punctuation-free, non-empty tokens
    """
    cleaned = []
    for tok in tokens:
        tok = tok.lower().strip()
        tok = re.sub(r"[^a-z\-]", "", tok)  # keep letters and hyphens
        if tok and len(tok) > 1:
            cleaned.append(tok)
    return cleaned


def clean_text(text):
    """Clean a raw text string (used before sentence segmentation)."""
    text = text.replace("\u00a0", " ")           # non-breaking spaces from PDFs
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


if __name__ == "__main__":
    print(clean_tokens(["Eligible", "beneficiaries,", "shall", "123", "be!!"]))
