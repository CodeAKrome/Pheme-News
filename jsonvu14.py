import curses
import json
import sys
import re  # Fixed missing import
from pathlib import Path
from collections import deque
import textwrap


def format_record(record, max_width=80):
    """Format the full record into lines for display."""
    lines = []

    def add_field(name, value):
        if value is None:
            return
        if isinstance(value, list) and not isinstance(value, str):
            if value and isinstance(value[0], dict):
                lines.append(f"{name}: [")
                for item in value:
                    for k, v in item.items():
                        lines.append(f"    {k}: {v}")
                lines.append("]")
            elif any(value):
                lines.append(f"{name}: {', '.join(map(str, value))}")
        else:
            lines.append(f"{name}: {value}")

    add_field("ID", record.get("id"))
    add_field("Lang", record.get("lang"))
    add_field("Source", record.get("source"))
    add_field("Title", record.get("title"))
    add_field("Link", record.get("link"))
    add_field("Published", record.get("published"))
    add_field("Summary", record.get("summary"))

    text = record.get("text")
    if text:
        lines.append("Text:")
        wrapped = textwrap.wrap(text, width=max_width - 4)
        for line in wrapped:
            lines.append("    " + line)

    ner = record.get("ner")
    if ner:
        lines.append("NER:")
        for sentence_data in ner:
            sentence = sentence_data.get("sentence", "")
            spans = sentence_data.get("spans", [])
            lines.append("    Sentence: " + sentence[:max_width - 12])
            for span in spans:
                span_text = span.get("text", "")
                span_value = span.get("value", "")
                if span_text and span_value:
                    lines.append(f"        Span: {span_text} -> {span_value}")

    return lines


def main(stdscr, file_path):
    # Initialize curses
    curses.curs_set(0)
    stdscr.timeout(100)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_YELLOW)

    max_y, max_x = stdscr.getmaxyx()
    display_height = max_y - 3
    display_win = stdscr.subwin(display_height, max_x, 0, 0)
    search_win = stdscr.subwin(1, max_x, display_height, 0)
    status_win = stdscr.subwin(1, max_x, display_height + 1, 0)

    # Load data
    records = []
    source_queue = deque()
    source_to_records = {}
    selected_ids = set()
    current_index = 0
    current_source_index = 0
    search_results = []
    is_searching = False
    search_query = ""

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f):
                try:
                    record = json.loads(line.strip())
                    records.append(record)
                except json.JSONDecodeError as e:
                    print(f"Skipping line {line_number + 1}: Invalid JSON — {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        sys.exit(1)

    records.sort(key=lambda r: r.get("id", 0))
    sources = sorted(set(r.get("source", "") for r in records))
    source_queue = deque(sources)
    for source in sources:
        source_to_records[source] = [
            i for i, r in enumerate(records) if r.get("source") == source
        ]

    def update_display():
        display_win.clear()
        if not records:
            display_win.addstr(0, 0, "No records found.", curses.color_pair(1))
        else:
            record = (
                search_results[current_index % len(search_results)]
                if is_searching and search_results
                else records[current_index % len(records)]
            )
            lines = format_record(record, max_x - 4)
            for i, line in enumerate(lines):
                if i >= display_height:
                    break
                try:
                    display_win.addstr(i, 0, line[:max_x - 1], curses.color_pair(1))
                except curses.error:
                    pass
        display_win.noutrefresh()

    def update_search():
        search_win.clear()
        search_win.addstr(0, 0, "Search: " + search_query[:max_x - 8], curses.color_pair(2))
        search_win.noutrefresh()

    def update_status(message=None):
        status_win.clear()
        text = message or (
            "Left/Right: Navigate | Up/Down: Cycle sources | Space: Select | Enter: Search | Esc: Clear | q: Quit"
        )
        status_win.addstr(0, 0, text[:max_x - 1], curses.color_pair(3))
        status_win.noutrefresh()

    update_display()
    update_search()
    update_status()
    curses.doupdate()

    while True:
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:
            break

        if key == -1:
            continue

        if key == ord("q"):
            break

        elif key == curses.KEY_LEFT:
            if is_searching and search_results:
                current_index = (current_index - 1) % len(search_results)
            else:
                current_index = (current_index - 1) % len(records)
            update_display()

        elif key == curses.KEY_RIGHT:
            if is_searching and search_results:
                current_index = (current_index + 1) % len(search_results)
            else:
                current_index = (current_index + 1) % len(records)
            update_display()

        elif key == curses.KEY_UP:
            if source_queue:
                current_source_index = (current_source_index - 1) % len(source_queue)
                source = source_queue[current_source_index]
                indices = source_to_records[source]
                if indices:
                    current_index = indices[0]
                    is_searching = False
                    search_query = ""
                    update_display()
                    update_search()

        elif key == curses.KEY_DOWN:
            if source_queue:
                current_source_index = (current_source_index + 1) % len(source_queue)
                source = source_queue[current_source_index]
                indices = source_to_records[source]
                if indices:
                    current_index = indices[0]
                    is_searching = False
                    search_query = ""
                    update_display()
                    update_search()

        elif key == ord(" "):  # Toggle selection
            record = (
                search_results[current_index % len(search_results)]
                if is_searching and search_results
                else records[current_index % len(records)]
            )
            record_id = record.get("id")
            if record_id in selected_ids:
                selected_ids.remove(record_id)
            else:
                selected_ids.add(record_id)
            update_display()

        elif key == 10:  # Enter to search
            query = search_query.strip().lower()
            if query:
                is_searching = True
                search_results = [
                    r for r in records
                    if (
                        re.search(query, str(r.get("id", "")), re.IGNORECASE) or
                        re.search(query, r.get("source", ""), re.IGNORECASE) or
                        re.search(query, r.get("title", ""), re.IGNORECASE) or
                        re.search(query, r.get("summary", ""), re.IGNORECASE) or
                        re.search(query, r.get("text", ""), re.IGNORECASE) or
                        any(
                            re.search(query, s.get("text", "").lower())
                            for sent in r.get("ner", [])
                            for s in sent.get("spans", [])
                        )
                    )
                ]
                current_index = 0
            else:
                is_searching = False
                search_results = []
                current_index = 0
            update_display()

        elif key == 27:  # Escape
            is_searching = False
            search_results = []
            search_query = ""
            current_index = 0
            update_display()
            update_search()

        elif 32 <= key <= 126:
            search_query += chr(key)
            update_search()

        elif key in (curses.KEY_BACKSPACE, 127):
            search_query = search_query[:-1]
            update_search()

        update_status()
        curses.doupdate()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python viewer.py <jsonl_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    curses.wrapper(main, file_path)
