"""
policy_analyzer.py
-------------------
Looks at the sentences of a policy document and sorts them into the
six categories a farmer cares about:

    who_can_apply, benefits, documents, how_to_apply, dates, conditions

This is done with simple keyword matching (no heavy ML model needed),
which keeps it easy to explain in a college presentation: "we scan
each sentence for words that signal a category, and score sentences
against every category."

NOT_MENTIONED is shown whenever a category has no matching sentence,
per the project requirement to never invent information.
"""

import re

from nlp.sentence_segmentation import segment_sentences
from nlp.keyword_extractor import extract_keywords

NOT_MENTIONED = "Not mentioned in the policy."

# Keyword signals for each policy category. Matching is done on the
# lowercase sentence text, so multi-word phrases work too.
CATEGORY_KEYWORDS = {
    "who_can_apply": [
        "eligible", "eligibility", "who can apply", "applicant must",
        "beneficiary", "beneficiaries", "small farmer", "marginal farmer",
        "shall be eligible", "criteria for", "qualify", "qualifying",
        "farmer who", "farmers who", "applicable to", "open to",
    ],
    "benefits": [
        "benefit", "financial assistance", "subsidy", "subsidies",
        "grant", "incentive", "amount of", "rs.", "rupees", "per acre",
        "per hectare", "assistance of", "support of", "loan", "insurance cover",
        "financial help", "compensation",
    ],
    "documents": [
        "document", "aadhaar", "aadhar", "certificate", "proof of",
        "copy of", "bank account", "land record", "7/12", "passbook",
        "identity proof", "income certificate", "photograph", "ration card",
    ],
    "how_to_apply": [
        "apply", "application", "submit", "register", "registration",
        "portal", "online", "offline", "form", "website", "office of",
        "district office", "block office", "common service centre", "csc",
        "component selection", "document submission", "preliminary scrutiny",
        "procurement", "execution", "post-verification", "sanction", "record verification",
    ],
    "dates": [
        "date", "deadline", "last date", "within", "before", "on or before",
        "commencing", "start date", "end date", "financial year", "valid till",
        "valid until", "closing date", "application period",
    ],
    "conditions": [
        "condition", "must", "mandatory", "shall not", "provided that",
        "subject to", "required to", "note that", "restriction",
        "not applicable", "only once", "maximum limit",
        "terms and conditions",
    ],
    "exclusions": [
        "not eligible", "shall not be eligible", "excluded", "exclusion",
        "not entitled", "shall not apply", "ineligible",
        "disqualified", "not covered", "shall not be covered",
        "exception", "debarred", "false information", "forged",
        "already subsidized", "outside the approved", "non-approved",
        "not possess", "not cultivate", "does not possess", "does not cultivate",
        "rejected", "false", "misleading", "returned for correction",
        "should not be claimed", "cannot be claimed",
    ],
    "verification": [
        "verification", "verify", "inspection", "geo-tag", "geo-tagged",
        "geo-tagging", "physical verification", "field inspection",
        "site visit", "audit", "validate", "validated", "cross-check",
    ],
    "payment_method": [
        "dbt", "direct benefit transfer", "transferred to", "credited to",
        "bank transfer", "installment", "instalment", "pfms", "neft",
        "direct transfer", "credited directly", "payment mode",
    ],
    "grievance": [
        "grievance", "complaint", "appeal", "redressal", "dispute",
        "objection", "review committee", "grievance redressal", "helpline",
        "toll free", "ombudsman", "escalate", "application status",
        "document deficiency", "implementation matters", "application number",
    ],
}

# A rough date pattern (e.g. "31st March 2024", "01/04/2024", "2024-25")
DATE_PATTERN = re.compile(
    r"\b(\d{1,2}(?:st|nd|rd|th)?\s+\w+\s+\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2,4})\b",
    re.IGNORECASE,
)

# Pattern for specific financial assistance lines (e.g. "40% ... Rs. 8,000")
FINANCIAL_PATTERN = re.compile(
    r'\d+\s*%.*?(?:Rs\.?|₹|rupees)\s*[\d,]+|(?:Rs\.?|₹|rupees)\s*[\d,]+.*?\d+\s*%',
    re.IGNORECASE,
)


def _score_sentence(sentence_lower, keywords):
    return sum(1 for kw in keywords if kw in sentence_lower)


def classify_sentences(sentences):
    """
    Assign each sentence to the category it best matches.

    Args:
        sentences (list[str])

    Returns:
        dict[str, list[str]]: category -> list of matching sentences
    """
    result = {category: [] for category in CATEGORY_KEYWORDS}

    for sentence in sentences:
        if sentence.startswith("Q:") or sentence.startswith("A:"):
            continue
            
        skip_prefixes = ("Policy Overview", "Objectives", "Simple Summary", "Financial assistance Component", "Frequently Asked Questions")
        if sentence.startswith(skip_prefixes):
            continue

        sentence_lower = sentence.lower()
        
        if "test document" in sentence_lower:
            continue
            
        if "maximum assistance" in sentence_lower and "farmer contribution" in sentence_lower:
            continue

        best_category = None
        best_score = 0
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = _score_sentence(sentence_lower, keywords)
            if category == "dates" and DATE_PATTERN.search(sentence):
                score += 2
            if category == "benefits" and FINANCIAL_PATTERN.search(sentence):
                score += 2
            if category == "payment_method" and any(w in sentence_lower for w in ["transferred", "paid", "remitted"]):
                score += 2
            if category == "verification" and any(w in sentence_lower for w in ["verified", "verify"]):
                score += 2
            if category == "conditions" and any(w in sentence_lower for w in ["must", "mandatory", "correct information"]):
                score += 2
            if category == "exclusions" and any(w in sentence_lower for w in ["rejected", "false", "misleading", "returned"]):
                score += 2
            if category == "grievance" and "grievance" in sentence_lower:
                score += 3
            if category == "dates" and any(w in sentence_lower for w in ["closing date", "application period"]):
                score += 2
            
            if score > best_score:
                best_score = score
                best_category = category

        if best_category and best_score > 0:
            result[best_category].append(sentence)

    return result


def analyze_policy(text):
    """
    Full analysis of a policy document's text.

    Args:
        text (str): raw policy text

    Returns:
        dict: {
            "sentences": [...],
            "categories": {category: [sentences]},
            "keywords": [(word, count), ...],
        }
    """
    sentences = segment_sentences(text)
    categories = classify_sentences(sentences)
    keywords = extract_keywords(text, top_n=12)

    return {
        "sentences": sentences,
        "categories": categories,
        "keywords": keywords,
    }
