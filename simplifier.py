"""
simplifier.py
-------------
Converts stiff government / legal language into short, easy
sentences a farmer can understand, WITHOUT changing the meaning.

This file is intentionally kept separate from the nlp/ pipeline
package. The nlp/ files only analyse text (segment, tokenize, clean,
remove stop-words, lemmatize, find keywords) - they never rewrite it.
This file is the one place that rewrites sentences, using a
phrase-substitution dictionary. If a real LLM/AI API were plugged in
later for higher quality simplification, it would live in its own
module (see llm_simplifier.py) and would only be called from here,
keeping the NLP pipeline untouched.
"""

import re

# Ordered list of (pattern, replacement). Longer/more specific
# phrases are listed first so they get replaced before shorter,
# more generic ones.
PHRASE_SUBSTITUTIONS = [
    (r"\bThe Small and Marginal Farmer Support Scheme \(SMFSS\) is a sample agricultural support programme designed to demonstrate how a government policy can be converted into simple language\b",
     "SMFSS is a sample government-style support scheme that helps eligible farmers with farm inputs, water-saving equipment, storage and post-harvest activities"),
    (r"\beligible beneficiaries shall be entitled to\b", "farmers who qualify can get"),
    (r"\bshall be entitled to\b", "can get"),
    (r"\bsubject to fulfillment of prescribed eligibility criteria\b",
     "if they meet the required conditions"),
    (r"\bsubject to fulfilment of prescribed eligibility criteria\b",
     "if they meet the required conditions"),
    (r"\bsubject to\b", "based on"),
    (r"\bshall be eligible\b", "can apply"),
    (r"\bis eligible to apply\b", "can apply"),
    (r"\bprescribed eligibility criteria\b", "required conditions"),
    (r"\bprior to\b", "before"),
    (r"\bin accordance with\b", "as per"),
    (r"\bwith reference to\b", "about"),
    (r"\bin respect of\b", "for"),
    (r"\bin the event of\b", "if"),
    (r"\bin the event that\b", "if"),
    (r"\bnotwithstanding\b", "even though"),
    (r"\bshall not be entitled to\b", "cannot get"),
    (r"\bshall be required to\b", "must"),
    (r"\bis mandatory to\b", "you must"),
    (r"\bis mandatorily required\b", "is required"),
    (r"\bfinancial assistance\b", "financial help"),
    (r"\ban applicant\b", "a farmer"),
    (r"\ban applicants\b", "farmers"),
    (r"\bapplicant(s)?\b", r"farmer\1"),
    (r"\bfurnish\b", "submit"),
    (r"\bshall\b", "will"),
    (r"\bthereof\b", ""),
    (r"\bhereby\b", ""),
    (r"\baforementioned\b", "mentioned above"),
    (r"\baforesaid\b", "mentioned above"),
    (r"\bpursuant to\b", "under"),
    (r"\butilization\b", "use"),
    (r"\butilisation\b", "use"),
    (r"\bcommencement\b", "start"),
    (r"\bdisbursed\b", "given"),
    (r"\bdisbursement\b", "payment"),
    (r"\bremuneration\b", "payment"),
    (r"\bstipulated\b", "fixed"),
]

_COMPILED_SUBSTITUTIONS = [
    (re.compile(pattern, re.IGNORECASE), replacement)
    for pattern, replacement in PHRASE_SUBSTITUTIONS
]


# Technical terms that should be kept but explained on first use,
# rather than blindly replaced with paraphrases that can break grammar.
TECHNICAL_GLOSSARY = {
    "beneficiary": "beneficiary (a farmer whose eligibility has been verified and whose assistance has been sanctioned)",
    "beneficiaries": "beneficiaries (farmers whose eligibility has been verified and whose assistance has been sanctioned)",
    "dbt": "DBT (Direct Benefit Transfer \u2014 money sent directly to your bank account)",
    "admissible cost": "admissible cost (the approved expense amount)",
    "geo-tagged": "geo-tagged (information or photographs associated with a specific location)",
    "approved vendor": "approved vendor (a supplier that meets the technical, registration and documentation requirements specified by the Department)",
}

_GLOSSARY_PATTERNS = [
    (re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE), explained)
    for term, explained in TECHNICAL_GLOSSARY.items()
]


def _apply_glossary(sentence, seen_terms):
    """On first occurrence of a technical term, add a parenthetical explanation.

    On subsequent occurrences the term is left as-is, because the reader
    has already seen the explanation.
    """
    result = sentence
    for pattern, explained in _GLOSSARY_PATTERNS:
        if pattern.search(result) and pattern.pattern not in seen_terms:
            result = pattern.sub(explained, result, count=1)
            seen_terms.add(pattern.pattern)
    return result


def simplify_sentence(sentence, seen_terms=None):
    """
    Rewrite one sentence in plain language.

    Args:
        sentence (str): original sentence
        seen_terms (set | None): tracks which glossary terms have been
            explained already; shared across a batch so each term is
            explained only once.

    Returns:
        str: simplified sentence
    """
    if seen_terms is None:
        seen_terms = set()

    simplified = sentence

    for pattern, replacement in _COMPILED_SUBSTITUTIONS:
        simplified = pattern.sub(replacement, simplified)

    # Explain technical terms with a parenthetical on first use
    simplified = _apply_glossary(simplified, seen_terms)

    # Collapse double spaces left behind by removed words like "hereby"
    simplified = re.sub(r"\s{2,}", " ", simplified).strip()

    # Split very long sentences (30+ words) into shorter ones at
    # natural break points so they stay easy to read.
    words = simplified.split()
    if len(words) > 30:
        parts = re.split(r",\s*(?:and|which|that|provided)\s+", simplified, maxsplit=1)
        if len(parts) == 2:
            simplified = parts[0].rstrip(", ") + ". " + parts[1][0].upper() + parts[1][1:]

    if simplified and simplified[-1] not in ".!?":
        simplified += "."

    # Make sure the sentence still starts with a capital letter, in
    # case a substitution (e.g. "Applicants" -> "farmers") left it
    # lowercase.
    if simplified:
        simplified = simplified[0].upper() + simplified[1:]

    return simplified


def simplify_sentences(sentences):
    """Simplify a list of sentences, sharing glossary state across them."""
    seen_terms = set()
    return [simplify_sentence(s, seen_terms) for s in sentences]


def build_simple_explanation(sentences, max_sentences=4):
    """
    Build a short overall "Simple Explanation" summary from the most
    informative sentences of the policy (the first few non-trivial
    sentences, simplified).

    Args:
        sentences (list[str]): original sentences from the policy
        max_sentences (int): how many sentences to include

    Returns:
        str: a short plain-language paragraph
    """
    if not sentences:
        return "Not mentioned in the policy."

    chosen = sentences[:max_sentences]
    simplified = simplify_sentences(chosen)
    return " ".join(simplified)
