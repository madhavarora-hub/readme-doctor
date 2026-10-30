#!/usr/bin/env python3
"""readme-doctor CLI: python cli.py README.md [--template]"""
import sys, json, re
from readme_doctor import CHECKS
from templater import suggest

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path = args[0] if args else "README.md"
    text = open(path, encoding="utf-8", errors="replace").read()
    if "--template" in sys.argv:
        print(suggest(text)); return
    score, fixes = 0, []
    for name, pat, fix, pts in CHECKS:
        if re.search(pat, text, re.M): score += pts
        else: fixes.append({"check": name, "fix": fix, "points": pts})
    print(json.dumps({"file": path, "score": score, "max": 100, "fixes": fixes}, indent=2))

if __name__ == "__main__":
    main()
