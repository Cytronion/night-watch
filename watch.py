"""Flag failed logins and off-hours successes in an auth log you supply.

Read-only. Does not connect to a host or attempt a login.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

FAIL = re.compile(r"failed password|authentication failure|invalid user|failed login", re.I)
OK = re.compile(r"accepted password|session opened|successful login", re.I)
USER = re.compile(r"(?:invalid user |for |user )([A-Za-z0-9._-]+)", re.I)
IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
STAMP = re.compile(r"\b(\d{2}):(\d{2}):(\d{2})\b")


def in_window(hour: int, start: int, end: int) -> bool:
    if start == end:
        return False
    if start < end:
        return start <= hour < end
    return hour >= start or hour < end


def read_lines(text: str, start: int = 22, end: int = 6) -> list[dict]:
    rows = []
    failures: dict[str, int] = defaultdict(int)
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        failed = bool(FAIL.search(line))
        success = bool(OK.search(line)) and not failed
        user = USER.search(line)
        ip = IP.search(line)
        stamp = STAMP.search(line)
        hour = int(stamp.group(1)) if stamp else None
        source = ip.group(0) if ip else (user.group(1) if user else "unknown")
        if failed:
            failures[source] += 1
        rows.append(
            {
                "line": number,
                "text": line,
                "failed": failed,
                "success": success,
                "user": user.group(1) if user else "",
                "source": source,
                "hour": hour,
                "off_hours": bool(success and hour is not None and in_window(hour, start, end)),
            }
        )
    for row in rows:
        row["repeat"] = row["failed"] and failures[row["source"]] >= 3
    return rows


def summarize(rows: list[dict]) -> dict:
    return {
        "lines": len(rows),
        "failed": sum(1 for row in rows if row["failed"]),
        "off_hours": sum(1 for row in rows if row["off_hours"]),
        "repeat_sources": sorted({row["source"] for row in rows if row["repeat"]}),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Read an auth log and flag failed or off-hours sign-ins.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--start", type=int, default=22)
    parser.add_argument("--end", type=int, default=6)
    args = parser.parse_args()
    rows = read_lines(args.path.read_text(), args.start, args.end)
    summary = summarize(rows)
    print(f"lines {summary['lines']}  failed {summary['failed']}  off-hours {summary['off_hours']}")
    if summary["repeat_sources"]:
        print("repeat sources:", ", ".join(summary["repeat_sources"]))
    for row in rows:
        if row["failed"] or row["off_hours"]:
            mark = "FAIL" if row["failed"] else "ODD "
            extra = " repeat" if row["repeat"] else ""
            print(f"{row['line']:>3}  {mark}{extra}  {row['text']}")


if __name__ == "__main__":
    main()
