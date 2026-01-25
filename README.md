# MVEL → English Agent (Ollama + LangChain)

This project converts MVEL rule files into clear, non-technical English explanations.

## What it does
- Parses MVEL `if / else if / else` rules
- Extracts decision branches
- Uses a local LLM via Ollama
- Outputs a human-readable explanation

## Run
```bash
python main.py examples/sample.mvel
