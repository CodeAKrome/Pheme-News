#!/usr/bin/env python3

import sys
import json
import time
from datetime import datetime, timedelta
import re


def parse_relative_time(relative_str):
    """Parse relative time strings like '-1 day', '-2 weeks', etc."""
    pattern = r"^-(\d+)\s+(day|days|week|weeks|hour|hours|minute|minutes)$"
    match = re.match(pattern, relative_str.strip())

    if not match:
        raise ValueError(f"Invalid relative time format: {relative_str}")

    amount = int(match.group(1))
    unit = match.group(2)

    # Normalize units
    if unit in ["day", "days"]:
        delta = timedelta(days=amount)
    elif unit in ["week", "weeks"]:
        delta = timedelta(weeks=amount)
    elif unit in ["hour", "hours"]:
        delta = timedelta(hours=amount)
    elif unit in ["minute", "minutes"]:
        delta = timedelta(minutes=amount)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")

    return datetime.now() - delta


def parse_absolute_date(date_str):
    """Parse absolute date in yyyymmddThhmmss format."""
    try:
        return datetime.strptime(date_str, "%Y%m%dT%H%M%S")
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Expected yyyymmddThhmmss")


def published_parsed_to_datetime(published_parsed):
    """Convert published_parsed array to datetime object."""
    if not published_parsed or len(published_parsed) < 6:
        return None

    year, month, day, hour, minute, second = published_parsed[:6]
    return datetime(year, month, day, hour, minute, second)


def main():
    if len(sys.argv) != 2:
        print("Usage: python program.py <date_filter>", file=sys.stderr)
        print("  <date_filter> can be:", file=sys.stderr)
        print(
            "    - Absolute date: yyyymmddThhmmss (e.g., 20250624T083154)",
            file=sys.stderr,
        )
        print(
            "    - Relative time: '-N unit' (e.g., '-1 day', '-2 weeks')",
            file=sys.stderr,
        )
        sys.exit(1)

    date_filter = sys.argv[1]

    try:
        # Determine if it's a relative time or absolute date
        if date_filter.startswith("-"):
            cutoff_date = parse_relative_time(date_filter)
        else:
            cutoff_date = parse_absolute_date(date_filter)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # Read JSON data from stdin
        for input_data in sys.stdin:
            input_data = input_data.strip()

            if not input_data:
                continue

            try:
                data = json.loads(input_data)
            except json.JSONDecodeError as e:
                print(
                    f"Error: json decode, continuing - {e}\ninput:\n->{input_data}<-\n",
                    file=sys.stderr,
                )
                continue

            # Check if data has published_parsed field
            if "published_parsed" not in data:
                print(
                    f"Error: no published_parsed field, continuing.\n{data['source'], data['id']}\n",
                    file=sys.stderr,
                )
                continue

            # Convert published_parsed to datetime
            article_date = published_parsed_to_datetime(data["published_parsed"])

            if article_date is None:
                print(
                    f"Error: Invalid published_parsed format, continuing. {data['source']} {data['id']} -{data['published_parsed']}-",
                    file=sys.stderr,
                )
                continue

            # Filter based on date comparison
            # For relative times (like '-1 day'), show articles newer than cutoff
            # For absolute dates, show articles newer than or equal to the specified date
            if date_filter.startswith("-"):
                # Relative time: show articles newer than cutoff_date
                if article_date >= cutoff_date:
                    print(input_data.strip())
                    # json.dump(data, sys.stdout, indent=2)
            else:
                # Absolute date: show articles newer than or equal to cutoff_date
                if article_date >= cutoff_date:
                    print(input_data.strip())
                    # json.dump(data, sys.stdout, indent=2)
    except Exception as e:
        print(f"Error: Bailing out: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
