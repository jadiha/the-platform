"""Run the whole pipeline after fetching: build every output, then check it.

Usage:
    uv run python -m pipeline.fetch      # once, or with --force to refresh
    uv run python -m pipeline.build
"""
from __future__ import annotations

from . import checks, ontario, people, toronto


def main() -> int:
    toronto.main()
    ontario.main()
    people.main()
    return checks.main()


if __name__ == "__main__":
    raise SystemExit(main())
