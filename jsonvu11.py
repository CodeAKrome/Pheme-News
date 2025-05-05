import curses
import json
import re
from pathlib import Path
from collections import deque
import textwrap


def truncate_text(text, max_length):
    """Truncate text and add ellipsis if too long."""
    return text[:max_length - 3] + "..." if len(text) > max_length else text


def format_record(record, max_width):
    """Format the full record into wrapped lines for display."""
    lines = []

    def add_field(name, value):
        if value:
            lines.append(f"{name}: {value[0] if isinstance(value, list) and value else value}")
            if isinstance(value, str) and len(value) > max_width:
                for wrapped_line in textwrap.wrap(value, width=max_width):
                    lines.append("    " + wrapped_line)
            elif isinstance(value, list) and isinstance(value[0], dict):
                lines[-1] += " ["
                for item in value:
                    lines.append("    - {}: {}".format(item.get('text', ''), item.get('value', '')))
                lines.append("    ]")

    add_field("ID", record.get("id"))
    add_field("Lang", record.get("lang"))
    add_field("Source", record.get("source"))
    add_field("Title", record.get("title"))
    add_field("Link", record.get("link"))
    add_field("Published", record.get("published"))
    add_field("Summary", record.get("summary"))
    add_field("Text", record.get("text"))
    add_field("NER", record.get("ner"))

    return lines


def main(stdscr):
    # Initialize curses
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Non-blocking input
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Normal
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Search bar
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_YELLOW) # Status bar

    # Window dimensions
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

    jsonl_file = Path("cache/dedupe.jsonl")  # Update path as needed
    if jsonl_file.exists():
        with jsonl_file.open() as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    records.append(record)
                except json.JSONDecodeError:
                    continue

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

            lines = format_record(record, max_x - 4)  # Leave space for margins
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
            "Left/Right: Navigate | Up/Down: Cycle sources | Space: Select | x: Export | Enter: Search | Esc: Clear | q: Quit"
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

        if key == -1:  # No input
            continue

        if key == ord("q"):
            break  # Exit on 'q'

        if key == curses.KEY_LEFT:
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
                if source_to_records[source]:
                    current_index = source_to_records[source][0]
                    is_searching = False
                    search_query = ""
                    update_display()
                    update_search()

        elif key == curses.KEY_DOWN:
            if source_queue:
                current_source_index = (current_source_index + 1) % len(source_queue)
                source = source_queue[current_source_index]
                if source_to_records[source]:
                    current_index = source_to_records[source][0]
                    is_searching = False
                    search_query = ""
                    update_display()
                    update_search()

        elif key == ord(" "):
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

        elif key == ord("x"):
            with open("ids.txt", "w") as f:
                for id in sorted(selected_ids):
                    f.write(f"{id}\n")
            update_status("Exported selected IDs to ids.txt")
            curses.doupdate()
            curses.napms(2000)
            update_status()

        elif key == 27:  # Escape
            is_searching = False
            search_results = []
            search_query = ""
            current_index = 0
            update_display()
            update_search()

        elif key == 10:  # Enter
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
                        any(re.search(query, s.get("text", ""), re.IGNORECASE) for s in r.get("ner", []))
                    )
                ]
                current_index = 0
            else:
                is_searching = False
                search_results = []
                current_index = 0
            update_display()

        elif 32 <= key <= 126:  # Printable characters
            search_query += chr(key)
            update_search()

        elif key == curses.KEY_BACKSPACE or key == 127:
            search_query = search_query[:-1]
            update_search()

        update_status()
        curses.doupdate()

if __name__ == "__main__":
    curses.wrapper(main)
