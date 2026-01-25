import re
from typing import Any, Dict, List

#remove comments 
RE_LINE_COMMENT = re.compile(r"//.*?$", re.MULTILINE)
RE_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)

#parses methods and variable names
IDENT_RE = re.compile(r"\b[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*\b")
ASSIGN_RE = re.compile(r"^\s*([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\s*=\s*(.+?);?\s*$")
RETURN_RE = re.compile(r"^\s*return\s+(.+?);?\s*$", re.IGNORECASE)

KEYWORDS = {
    "if", "else", "return", "true", "false", "null", "new",
    "for", "while", "switch", "case", "break", "continue",
}

def strip_comments(src: str) -> str:
    src = RE_BLOCK_COMMENT.sub("", src)
    src = RE_LINE_COMMENT.sub("", src)
    return src

def parse_mvel_branches(mvel_text: str) -> Dict[str, Any]:
    src = strip_comments(mvel_text)
    branches = []
    variables = set()
    outputs = set()

    lines = src.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("if") or line.startswith("else if"):
            condition = line[line.find("(")+1:line.rfind(")")]
            i += 1
            actions = []

            while i < len(lines) and "}" not in lines[i]:
                l = lines[i].strip()
                if "=" in l:
                    outputs.add(l.split("=")[0].strip())
                    actions.append(l.rstrip(";"))
                i += 1

            branches.append({
                "condition": condition.strip(),
                "actions": actions
            })

        elif line.startswith("else"):
            i += 1
            actions = []
            while i < len(lines) and "}" not in lines[i]:
                l = lines[i].strip()
                if "=" in l:
                    outputs.add(l.split("=")[0].strip())
                    actions.append(l.rstrip(";"))
                i += 1

            branches.append({
                "condition": "DEFAULT",
                "actions": actions
            })

        for ident in IDENT_RE.findall(line):
            if ident not in KEYWORDS:
                variables.add(ident)

        i += 1

    return {
        "branches": branches,
        "variables": sorted(list(variables)),
        "outputs": sorted(list(outputs))
    }
