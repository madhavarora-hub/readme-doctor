#!/usr/bin/env python3
"""readme-doctor: score a README.md and list concrete fixes. Usage: python readme_doctor.py [path]"""
import re, sys, json

CHECKS = [
    ("title", r"^#\s+\S+", "Add a top-level '# Title' heading.", 10),
    ("description", r"(?m)^(?!#)(?!\s*$).{40,}", "Add a 1-2 sentence description of what the project does.", 15),
    ("install", r"(?i)\b(install|pip install|npm install|setup)\b", "Add an Installation section.", 15),
    ("usage", r"(?i)\b(usage|example|quick ?start)\b", "Add a Usage/Quick start section with a code example.", 20),
    ("code_block", r"```", "Include at least one fenced code block.", 10),
    ("license", r"(?i)\blicen[sc]e\b", "State the license.", 10),
    ("contributing", r"(?i)\bcontribut", "Add contribution guidelines.", 5),
    ("badges", r"!\[[^\]]*\]\(https?://[^)]*\)", "Add a badge or screenshot.", 5),
    ("sections", r"(?m)^##\s+\S+", "Use '##' sections to structure the document.", 10),
]

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "README.md"
    text = open(path, encoding="utf-8", errors="replace").read()
    score, fixes = 0, []
    for name, pat, fix, pts in CHECKS:
        if re.search(pat, text, re.M):
            score += pts
        else:
            fixes.append({"check": name, "fix": fix, "points": pts})
    print(json.dumps({"file": path, "score": score, "max": 100, "fixes": fixes}, indent=2))

if __name__ == "__main__":
    main()
