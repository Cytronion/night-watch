# Night Watch

A defensive reader for authentication logs. Paste a log, or open a file you already have. It marks failed sign-ins, repeated failures from the same source, and successes that fall outside the hours you set.

It does not connect to a server, scan a network, or try passwords. The only input is the text you give it.

Open `index.html` in a browser. A sample college-lab log is loaded so the docket is not empty.

## What it flags

- Failed login lines (`Failed password`, `authentication failure`, `Invalid user`, `FAILED LOGIN`)
- A source with three or more failures in the file
- A successful login outside the watch window (default 22:00–06:00)

Hours are interpreted on a 24-hour clock in the log’s own timestamps. The window can cross midnight.

## Run the Python core

```bash
python3 watch.py sample.log
python3 watch.py sample.log --start 23 --end 5
```

`watch.py` uses the same rules as the page.

## Sample

`sample.log` is invented syslog-style text for a lab account named `lab`. No real addresses.

## Stack

HTML, CSS, and JavaScript for the night-desk docket. Python 3 for the checker. No packages.
