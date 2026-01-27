import re
from typing import Any, Dict

RE_LINE_COMMENT = re.compile(r"//.*?$", re.MULTILINE)
RE_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)

IDENT_RE = re.compile(r"\b[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*\b")

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
        raw_line = lines[i].strip()
        # normalize: allow patterns like "} else if (...)" and "} else {"
        line = raw_line.lstrip("}").strip()

        # collect identifiers from the normalized line
        for ident in IDENT_RE.findall(line):
            if ident not in KEYWORDS:
                variables.add(ident)

        if line.startswith("if") or line.startswith("else if"):
            condition = line[line.find("(") + 1 : line.rfind(")")] if "(" in line and ")" in line else ""
            i += 1
            actions = []

            # read action lines until we hit a line containing "}"
            while i < len(lines) and "}" not in lines[i]:
                l = lines[i].strip()
                if "=" in l:
                    outputs.add(l.split("=")[0].strip())
                    actions.append(l.rstrip(";"))
                i += 1

            branches.append({"condition": condition.strip(), "actions": actions})

            # IMPORTANT: do NOT i += 1 here.
            # We want to re-process the same line that contains "}" (it might be "} else if ...")
            continue

        if line.startswith("else"):
            # else branch has no condition -> DEFAULT
            i += 1
            actions = []

            while i < len(lines) and "}" not in lines[i]:
                l = lines[i].strip()
                if "=" in l:
                    outputs.add(l.split("=")[0].strip())
                    actions.append(l.rstrip(";"))
                i += 1

            branches.append({"condition": "DEFAULT", "actions": actions})
            # same idea: re-process closing line if it contains chained else (rare)
            continue

        i += 1

    return {
        "branches": branches,
        "variables": sorted(variables),
        "outputs": sorted(outputs),
    }
