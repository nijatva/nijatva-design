#!/usr/bin/env python3
"""Check that every shared-strings file carries the same keys.

strings/common-<lang>.xml must all have identical <string name="..."> keys, every
key must start with nj_, and no string may be empty.

Usage: python3 scripts/check_strings.py
Exit 1 on any failure (CI gate).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STRINGS = ROOT / "strings"
KEY_RE = re.compile(r'<string\s+name="([^"]+)"\s*>(.*?)</string>', re.S)


def load(path: Path) -> dict[str, str]:
    return {m.group(1): m.group(2).strip() for m in KEY_RE.finditer(path.read_text())}


def main() -> int:
    files = sorted(STRINGS.glob("common-*.xml"))
    if not files:
        print("no strings/common-*.xml found", file=sys.stderr)
        return 2
    data = {f.stem.replace("common-", ""): load(f) for f in files}
    base_lang = "en" if "en" in data else sorted(data)[0]
    base = data[base_lang]
    problems = []

    for key in base:
        if not key.startswith("nj_"):
            problems.append(f"{base_lang}: key '{key}' does not start with nj_")
    for key, value in base.items():
        if not value:
            problems.append(f"{base_lang}: '{key}' is empty")

    for lang, strings in data.items():
        if lang == base_lang:
            continue
        missing = sorted(set(base) - set(strings))
        extra = sorted(set(strings) - set(base))
        empty = sorted(k for k, v in strings.items() if not v)
        if missing:
            problems.append(f"{lang}: missing {len(missing)} keys: {', '.join(missing[:5])}")
        if extra:
            problems.append(f"{lang}: {len(extra)} keys not in {base_lang}: {', '.join(extra[:5])}")
        if empty:
            problems.append(f"{lang}: empty values: {', '.join(empty[:5])}")

    for p in problems:
        print("FAIL", p)
    total = ", ".join(f"{lang}={len(v)}" for lang, v in sorted(data.items()))
    print(f"\n{len(data)} languages, keys per file: {total}")
    print("clean" if not problems else f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
