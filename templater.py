#!/usr/bin/env python3
"""Generate README skeleton sections for checks that failed. Usage: python templater.py README.md"""
import re, sys
from readme_doctor import CHECKS

SNIPPETS = {
    "title": "# Project Title\n",
    "description": "One or two sentences describing what this project does and who it is for.\n",
    "install": "## Installation\n\n```\npip install your-package\n```\n",
    "usage": "## Usage\n\n```\nyour-command --example\n```\n",
    "code_block": "```\n# example\n```\n",
    "license": "## License\n\nMIT\n",
    "contributing": "## Contributing\n\nPull requests are welcome. Open an issue first to discuss changes.\n",
    "badges": "![build](https://img.shields.io/badge/build-passing-green)\n",
    "sections": "## Overview\n",
}

def missing(text):
    return [n for n, pat, _, _ in CHECKS if not re.search(pat, text, re.M)]

def suggest(text):
    return "\n".join(SNIPPETS[n] for n in missing(text) if n in SNIPPETS)

if __name__ == "__main__":
    print(suggest(open(sys.argv[1], encoding="utf-8", errors="replace").read()))
