import subprocess
import sys
import shlex

def run_llm(prompt: str) -> str:
    """
    Runs a local LLM using subprocess and returns ONLY model output text.
    Adjust the command for your local model.

    Example command (Ollama):
      ollama run llama3.1:7b --prompt "extract only code"
    """

    final_prompt = f"Extract only the programming code from the following OCR text:\n\n{prompt}"

    result = subprocess.run(
        ["ollama", "run", "llama3.1:7b", "--prompt", final_prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode != 0:
        raise RuntimeError(f"Ollama failed: {result.stderr.decode()}")

    return result.stdout.decode().strip()

if __name__ == "__main__":
    input_text = sys.stdin.read()
    print(run_llm(input_text))