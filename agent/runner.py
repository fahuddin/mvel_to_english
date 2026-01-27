# agent/runner.py
import json
from typing import List

from agent.llm import get_llm
from agent.memory import load_memory, format_context_from_memory
from agent.tracing import Trace

from agent.tools.mvel_parser_tool import parse_mvel_branches
from agent.tools.static_checker_tool import run_static_checks
from agent.tools.rag import retrieve_context

from agent.agents.planner import plan_steps
from agent.agents.explainer import explain_rule
from agent.agents.verifier import verify_explanation, rewrite_explanation
from agent.agents.diff import diff_rules
from agent.agents.tests import generate_tests


def run(mode: str, mvel_texts: List[str], model: str, enable_trace: bool) -> str:
    """
    Orchestrates the agent system.

    Args:
        mode: "explain" | "verify" | "tests" | "diff" | "agentic"
        mvel_texts: list of raw MVEL strings (1 item for most modes, 2 for diff)
        model: Ollama model name
        enable_trace: whether to write a run trace JSON file under runs/

    Returns:
        Final output string (English explanation, diff explanation, or JSON test cases)
    """
    # 1) Initialize shared resources
    llm = get_llm(model=model, temperature=0.0)  # deterministic
    mem = load_memory() #load user settings and domain mapping 
    mem_context = format_context_from_memory(mem)  

    trace = Trace(enabled=enable_trace)
    trace.log_step("start", {"mode": mode, "model": model, "inputs": len(mvel_texts)})

    # 2) Ask planner for the execution plan
    steps = plan_steps(llm, mode)
    trace.log_step("plan", {"steps": steps})

    # 3) Shared working state (short-term memory for this run)
    extractions: List[dict] = []
    context: str = ""
    english: str = ""           # holds the current natural-language output
    verdict: dict = {}          # holds verifier output when used
    static_issues: List[str] = []

    # 4) Execute the plan
    for step in steps:
        if step == "parse":
            idx = len(extractions)
            if idx >= len(mvel_texts):
                trace.log_step("parse_skipped", {"reason": "no more inputs", "idx": idx})
                continue

            extraction = parse_mvel_branches(mvel_texts[idx])
            extractions.append(extraction)

            trace.log_step("parse", {
                "index": idx,
                "branches": len(extraction.get("branches", [])),
                "outputs": extraction.get("outputs", []),
            })

        elif step == "static_checks":
            if not extractions:
                static_issues = ["static_checks: no extraction available (parse not run yet)."]
            else:
                static_issues = run_static_checks(extractions[-1])

            trace.log_step("static_checks", {"issues": static_issues})

        elif step == "retrieve_context":
            # Simple RAG + memory context
            # Uses first MVEL text as query signal (good enough for POC)
            rag = retrieve_context(mvel_texts[0] if mvel_texts else "", kb_dir="dir")
            pieces = []
            if mem_context:
                pieces.append(mem_context)
            if rag:
                pieces.append(rag)
            if static_issues:
                pieces.append("Static check notes:\n" + "\n".join(f"- {x}" for x in static_issues))

            context = "\n\n".join(pieces).strip()
            trace.log_step("retrieve_context", {"context_chars": len(context)})

        elif step == "explain":
            if not extractions:
                english = "Could not parse any rule branches from the provided MVEL."
                trace.log_step("explain_fallback", {"reason": "no extraction"})
                continue

            english = explain_rule(llm, extractions[-1], context)
            trace.log_step("explain", {"english_chars": len(english)})

        elif step == "verify":
            if not extractions or not english:
                verdict = {"ok": False, "missing": ["verify: missing extraction or english"], "rewrite_needed": True}
            else:
                verdict = verify_explanation(llm, extractions[-1], english)

            trace.log_step("verify", verdict)

        elif step == "rewrite":
            # Only rewrite if verifier says it's not OK
            if verdict.get("ok") is False and extractions and english:
                english = rewrite_explanation(llm, extractions[-1], english, verdict.get("missing", []))
                trace.log_step("rewrite", {"english_chars": len(english)})
            else:
                trace.log_step("rewrite_skipped", {"ok": verdict.get("ok", True)})

        elif step == "generate_tests":
            if not extractions:
                tests_json = [{"name": "error", "input": {}, "expected": {}, "note": "No extraction available"}]
            else:
                tests_json = generate_tests(llm, extractions[-1])

            english = json.dumps(tests_json, ensure_ascii=False, indent=2)
            trace.log_step("generate_tests", {"count": len(tests_json)})

        elif step == "diff":
            if len(extractions) < 2:
                english = "Diff requires two parsed rules, but fewer were available."
                trace.log_step("diff_fallback", {"reason": "need 2 extractions", "got": len(extractions)})
            else:
                english = diff_rules(llm, extractions[0], extractions[1])
                trace.log_step("diff", {"english_chars": len(english)})

        else:
            trace.log_step("unknown_step", {"step": step})

    # 5) Finalize and write trace
    if not english:
        english = "No output was produced. Check the plan and earlier steps."

    trace.finish(english)
    trace.write()
    return english
