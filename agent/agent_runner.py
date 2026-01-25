import json
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser

from agent.mvel_parser import parse_mvel_branches
from agent.prompts import ENGLISH_PROMPT

def run_agent(mvel_text: str, model: str = "llama3.1") -> str:
    parsed = parse_mvel_branches(mvel_text)

    llm = ChatOllama(
        model=model,
        temperature=0.0
    )

    chain = ENGLISH_PROMPT | llm | StrOutputParser()

    english = chain.invoke({
        "extraction": json.dumps(parsed, indent=2)
    })

    return english.strip()
