"""
app.py
------
Main Flask application for Krishi Saral.

Flow (matches the required user flow exactly):
    Upload PDF / Paste Text  ->  Analyze  ->  Simple Explanation

Routes:
    GET  /          -> home page (upload PDF or paste text)
    POST /analyze    -> runs the pipeline and shows the result page

Everything shown on the result page is either:
    (a) directly derived from the uploaded policy text, or
    (b) the literal string "Not mentioned in the policy."
No information is ever invented.
"""

from flask import Flask, render_template, request

from pdf_extractor import extract_text_from_pdf, PDFExtractionError
from policy_analyzer import analyze_policy, NOT_MENTIONED
from simplifier import simplify_sentences, build_simple_explanation
from translator import get_labels, translate_text

# Set this to True (and set ANTHROPIC_API_KEY) to use llm_simplifier.py
# instead of the default rule-based simplifier.py. Kept as a single,
# clearly-labelled switch so the separation is obvious in the demo.
USE_LLM_SIMPLIFIER = False

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024  # 15 MB upload limit


CATEGORY_ORDER = [
    "who_can_apply",
    "benefits",
    "documents",
    "how_to_apply",
    "dates",
    "conditions",
    "exclusions",
    "verification",
    "payment_method",
    "grievance",
]


def _simplify(sentences, language):
    """Simplify sentences using the rule-based simplifier by default,
    or the optional LLM simplifier if it has been switched on."""
    if USE_LLM_SIMPLIFIER:
        try:
            from llm_simplifier import llm_simplify, is_available
            if is_available():
                return llm_simplify(sentences, language=language)
        except Exception:
            pass  # fall back to rule-based simplifier below
    return simplify_sentences(sentences)


def _build_result(policy_text, language):
    """Run the full pipeline and build everything the template needs."""
    analysis = analyze_policy(policy_text)
    categories = analysis["categories"]

    simple_explanation = build_simple_explanation(analysis["sentences"])
    simple_explanation = translate_text([simple_explanation], language)[0]

    section_results = {}
    for category in CATEGORY_ORDER:
        raw_sentences = categories.get(category, [])
        if raw_sentences:
            simplified = _simplify(raw_sentences, language)
            simplified = translate_text(simplified, language)
            section_results[category] = simplified
        else:
            section_results[category] = [translate_text([NOT_MENTIONED], language)[0]]

    return {
        "simple_explanation": simple_explanation,
        "sections": section_results,
        "keywords": [kw for kw, _count in analysis["keywords"]],
        "sentence_count": len(analysis["sentences"]),
    }


@app.route("/")
def home():
    labels = get_labels("English")
    return render_template("index.html", labels=labels, language="English")


@app.route("/analyze", methods=["POST"])
def analyze():
    language = request.form.get("language", "English")
    labels = get_labels(language)

    policy_text = ""
    error = None

    uploaded_file = request.files.get("policy_pdf")
    pasted_text = request.form.get("policy_text", "").strip()

    if uploaded_file and uploaded_file.filename:
        try:
            policy_text = extract_text_from_pdf(uploaded_file.stream)
        except PDFExtractionError as e:
            error = str(e)
    elif pasted_text:
        policy_text = pasted_text
    else:
        error = "Please upload a PDF or paste some policy text before analyzing."

    if error:
        home_labels = get_labels("English")
        return render_template("index.html", labels=home_labels, language="English", error=error)

    result = _build_result(policy_text, language)

    return render_template(
        "result.html",
        labels=labels,
        language=language,
        result=result,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
