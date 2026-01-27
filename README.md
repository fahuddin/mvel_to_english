# MVEL → English Agent (Ollama + LangChain)

An agentic AI system that parses MVEL business rules, explains them in plain English, verifies correctness, generates test cases and self-corrects using reflection 

## What it does
- Parses MVEL `if / else if / else` rules
- Extracts decision branches
- Uses a local LLM via Ollama
- Outputs a human-readable explanation

🧠 Why This Is Agentic AI

This system demonstrates true agentic behavior:

🧭 Planning – dynamically selects execution steps

🛠️ Tool use – parser, RAG, checker, coverage, etc.

🔍 Self-verification – checks its own explanations

🔁 Self-correction – rewrites when wrong

🪞 Reflection – critiques final output

🧠 Memory – persists lessons across runs

📊 Observability – full execution traces

This goes far beyond “prompt → response”.



agentic_ai/
├── main.py
├── agent/
│   ├── runner.py              # Orchestrator
│   ├── llm.py                 # LLM loader (Ollama)
│   ├── memory.py              # Persistent memory
│   ├── tracing.py             # Run tracing
│   ├── types.py               # Agent schemas
│   ├── agents/
│   │   ├── planner.py
│   │   ├── explainer.py
│   │   ├── verifier.py
│   │   ├── reflect.py
│   │   ├── tests.py
│   │   └── diff.py
│   └── tools/
│       ├── mvel_parser_tool.py
│       ├── static_checker_tool.py
│       ├── rag.py
|       |── dir/                # Knowledge base for RAG
├── runs/                       # Execution traces
└── examples/
    └── rule.mvel



## Run
```bash
python main.py examples/sample.mvel


python main.py --mode explain examples/rule.mvel
Verify explanation fidelity
python main.py --mode verify examples/rule.mvel
Generate test cases
python main.py --mode tests examples/rule.mvel
Diff two rules
python main.py --mode diff old.mvel new.mvel