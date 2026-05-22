"""Command-line interface for logslice."""

import argparse
import sys
from typing import Optional

from logslice.log_reader import slice_log
from logslice.timestamp_parser import parse_datetime_arg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Fast log filtering and time-range extraction tool.",
    )
    parser.add_argument(
        "source",
        nargs="?",
        default="-",
        help="Log file path or '-' to read from stdin (default: stdin).",
    )
    parser.add_argument(
        "-s", "--start",
        metavar="DATETIME",
        default=None,
        help="Include lines at or after this timestamp (ISO 8601 or common log formats).",
    )
    parser.add_argument(
        "-e", "--end",
        metavar="DATETIME",
        default=None,
        help="Include lines at or before this timestamp.",
    )
    parser.add_argument(
        "-f", "--follow",
        action="store_true",
        default=False,
        help="After reaching --start, emit all subsequent lines (ignore --end).",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8).",
    )
    return parser


def run(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    start_dt = None
    end_dt = None

    if args.start:
        try:
            start_dt = parse_datetime_arg(args.start)
        except ValueError as exc:
            print(f"logslice: invalid --start value: {exc}", file=sys.stderr)
            return 2

    if args.end:
        try:
            end_dt = parse_datetime_arg(args.end)
        except ValueError as exc:
            print(f"logslice: invalid --end value: {exc}", file=sys.stderr)
            return 2

    if start_dt and end_dt and start_dt > end_dt:
        print("logslice: --start must not be later than --end", file=sys.stderr)
        return 2

    try:
        for line in slice_log(
            source=args.source,
            start=start_dt,
            end=end_dt,
            follow=args.follow,
            encoding=args.encoding,
        ):
            sys.stdout.write(line)
    except FileNotFoundError:
        print(f"logslice: file not found: {args.source}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        pass

    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
