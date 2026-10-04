"""
llm_simplifier.py
------------------
OPTIONAL component. Not used by default.

The project requirement says: "If an AI/LLM API is used for text
simplification, keep that component clearly separated from the NLP
preprocessing pipeline." This file is that clearly-separated
component.

By default the app uses simplifier.py (rule-based, offline, fully
explainable). If you want to try higher-quality simplification using
Anthropic's Claude API instead, set an ANTHROPIC_API_KEY environment
variable and switch USE_LLM_SIMPLIFIER = True in app.py.

Nothing in nlp/ or policy_analyzer.py ever imports this file - only
app.py decides whether to call it, and only for the rewriting step.
"""

import os

try:
    import anthropic
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False


def is_available():
    """Whether the LLM simplifier can actually be used right now."""
    return _SDK_AVAILABLE and bool(os.environ.get("ANTHROPIC_API_KEY"))


def llm_simplify(sentences, language="English"):
    """
    Ask an LLM to simplify a list of policy sentences into plain
    language, without changing their meaning.

    Args:
        sentences (list[str]): original sentences
        language (str): "English" or "Marathi"

    Returns:
        list[str]: simplified sentences (same order/length as input)
    """
    if not is_available():
        raise RuntimeError(
            "LLM simplifier is not configured. Set ANTHROPIC_API_KEY "
            "to use it, or use the default rule-based simplifier.py instead."
        )

    client = anthropic.Anthropic()
    joined = "\n".join(f"{i+1}. {s}" for i, s in enumerate(sentences))

    prompt = (
        f"Rewrite each of the following government policy sentences in "
        f"very simple {language}, for a rural farmer with limited "
        f"education. Keep the meaning exactly the same. Do not add new "
        f"information. Reply with one simplified sentence per line, in "
        f"the same order, no numbering:\n\n{joined}"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    text = "".join(
        block.text for block in response.content if getattr(block, "type", "") == "text"
    )
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]

    # Safety net: if the LLM returned a different number of lines,
    # fall back to the originals rather than risk misaligned output.
    if len(lines) != len(sentences):
        return sentences
    return lines
