import time

def ask(question: str) -> str:
    """Mock LLM response."""
    time.sleep(0.5)
    return f"This is an AI response to: {question}"
