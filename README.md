# logslice

> Fast log filtering and time-range extraction tool for structured and unstructured logs

---

## Installation

```bash
pip install logslice
```

---

## Usage

Extract logs within a specific time range:

```bash
logslice --input app.log --start "2024-01-15 08:00:00" --end "2024-01-15 09:00:00"
```

Filter logs by keyword and output to a file:

```bash
logslice --input app.log --filter "ERROR" --output errors.log
```

Use it as a Python library:

```python
from logslice import LogSlicer

slicer = LogSlicer("app.log")
results = slicer.slice(start="2024-01-15 08:00:00", end="2024-01-15 09:00:00")

for line in results:
    print(line)
```

### Options

| Flag | Description |
|------|-------------|
| `--input` | Path to the log file |
| `--start` | Start of the time range |
| `--end` | End of the time range |
| `--filter` | Keyword or regex pattern to filter lines |
| `--output` | Write results to a file instead of stdout |
| `--format` | Log timestamp format (default: auto-detect) |

---

## Features

- Supports structured (JSON) and unstructured (plain text) log formats
- Auto-detects common timestamp formats
- Regex-based filtering
- Handles large log files efficiently with streaming reads

---

## License

This project is licensed under the [MIT License](LICENSE).