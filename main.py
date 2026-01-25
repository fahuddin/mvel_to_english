"""
main.py is just a CLI wrapper: 
it reads an MVEL file from disk, 
picks an Ollama model name, 
calls run_agent, 
and prints the English.
"""
import sys
from agent.agent_runner import run_agent

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py path/to/rule.mvel [model]")
        sys.exit(1)

    path = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "llama3.1"

    with open(path, "r", encoding="utf-8") as f:
        mvel_text = f.read()

    english = run_agent(mvel_text, model=model)
    print("\n" + english + "\n")

if __name__ == "__main__":
    main()
