import curses
import json
import re
from pathlib import Path
from collections import deque

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

    # Load and filter JSONL data
    records = []
    source_queue = deque()
    source_to_records = {}
    selected_ids = set()
    current_index = 0
    current_source_index = 0
    search_results = []
    is_searching = False
    search_query = ""

    jsonl_file = Path("cache/dedupe.jsonl")
    if jsonl_file.exists():
        with jsonl_file.open() as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    filtered_spans = [
                        span for span in [
                            s for n in record.get("ner", []) for s in n.get("spans", [])
                        ]
                        if span.get("value") == "GPE" and span.get("text") in ["China", "Vietnam"]
                    ]
                    if filtered_spans:
                        record["filtered_spans"] = filtered_spans
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
            selected = "Selected" if record.get("id") in selected_ids else "Not Selected"
            spans_text = "\n".join(
                f"  - {s['text']}: {s['value']}" for s in record.get("filtered_spans", [])
            )
            text = (
                f"ID: {record.get('id', 'N/A')} ({selected})\n"
                f"Source: {record.get('source', 'N/A')}\n"
                f"Title: {record.get('title', 'N/A')}\n"
                f"Spans:\n{spans_text}"
            )
            lines = text.split("\n")
            for i, line in enumerate(lines[:display_height]):
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
            "Left/Right: Navigate | Up/Down: Cycle sources | "
            "Space: Select | x: Export | Enter: Search | Esc: Clear"
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
            update_status("Exported IDs to ids.txt")
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
                        re.search(query, str(r.get("id", "")).lower()) or
                        re.search(query, r.get("source", "").lower()) or
                        re.search(query, r.get("title", "").lower()) or
                        any(re.search(query, s.get("text", "").lower()) for s in r.get("filtered_spans", []))
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

        curses.doupdate()

if __name__ == "__main__":
    curses.wrapper(main)
