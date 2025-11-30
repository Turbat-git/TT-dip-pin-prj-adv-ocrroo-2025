import subprocess
import sys
import json
import shlex

def run_llm(prompt: str) -> str:
    """
    Runs a local LLM using subprocess and returns ONLY model output text.
    Adjust the command for your local model.

    Example command (Ollama):
      ollama run codellama:7b --prompt "extract only code"
    """

    # Build full prompt
    final_prompt = f"""
You are a code extraction engine.
Given OCR text, return ONLY the code blocks found.
Do NOT rewrite, fix, explain, or comment.
If no code exists, return an empty string.

OCR TEXT:
{prompt}
"""

    # Example using Ollama
    cmd = f'ollama run codellama "{final_prompt}"'

    try:
        result = subprocess.run(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=45
        )
    except Exception as e:
        return f"LLM ERROR: {e}"

    if result.returncode != 0:
        return f"LLM ERROR: {result.stderr}"

    return result.stdout.strip()


if __name__ == "__main__":
    # If used as a CLI tool:
    input_text = sys.stdin.read()
    print(run_llm(input_text))