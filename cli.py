#!/usr/bin/env python3
"""readme-doctor CLI: python cli.py README.md [--template] [--min-score N] [--format md]"""
import sys, json, re
from readme_doctor import CHECKS
from templater import suggest

def evaluate(text):
    score, fixes = 0, []
    for name, pat, fix, pts in CHECKS:
        if re.search(pat, text, re.M): score += pts
        else: fixes.append({"check": name, "fix": fix, "points": pts})
    return score, fixes

def to_markdown(path, score, fixes):
    lines = [f"# README report: {path}", "", f"**Score: {score}/100**", ""]
    lines += [f"- [ ] {f['fix']} (+{f['points']})" for f in fixes] or ["No fixes needed."]
    return "\n".join(lines)

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    min_score = None; fmt = "json"; args = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--min-score": min_score = int(argv[i+1]); i += 1
        elif a == "--format": fmt = argv[i+1]; i += 1
        elif not a.startswith("--"): args.append(a)
        i += 1
    path = args[0] if args else "README.md"
    text = open(path, encoding="utf-8", errors="replace").read()
    if "--template" in argv:
        print(suggest(text)); return 0
    score, fixes = evaluate(text)
    if fmt == "md": print(to_markdown(path, score, fixes))
    else: print(json.dumps({"file": path, "score": score, "max": 100, "fixes": fixes}, indent=2))
    return 1 if (min_score is not None and score < min_score) else 0

if __name__ == "__main__":
    sys.exit(main())
