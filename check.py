"""Checks for the auth-log reader. Run: python3 check.py"""

from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("watch", ROOT / "watch.py")
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)


def main() -> None:
    sample = (ROOT / "sample.log").read_text()
    rows = watch.read_lines(sample)
    summary = watch.summarize(rows)
    assert summary == {
        "lines": 10,
        "failed": 5,
        "off_hours": 1,
        "repeat_sources": ["172.16.8.40"],
    }
    day = [row for row in watch.read_lines(sample, start=9, end=12) if row["off_hours"]]
    assert len(day) == 2
    assert any("09:14" in row["text"] for row in day)
    assert any("11:02" in row["text"] for row in day)
    assert watch.summarize(watch.read_lines(""))["lines"] == 0
    night = watch.read_lines(
        "Oct  5 02:10:00 lab sshd[1]: Accepted password for dev from 10.1.1.1 port 22 ssh2\n"
    )
    assert night[0]["off_hours"]
    burst = watch.read_lines(
        "\n".join(
            [
                "Oct  5 10:00:01 lab sshd[1]: Failed password for a from 10.9.9.9 port 1 ssh2",
                "Oct  5 10:00:02 lab sshd[1]: Failed password for a from 10.9.9.9 port 1 ssh2",
                "Oct  5 10:00:03 lab sshd[1]: authentication failure for a from 10.9.9.9",
            ]
        )
    )
    assert all(row["repeat"] for row in burst)
    assert watch.in_window(22, 22, 6) and watch.in_window(5, 22, 6)
    assert not watch.in_window(6, 22, 6)
    print("all checks passed")


if __name__ == "__main__":
    main()
