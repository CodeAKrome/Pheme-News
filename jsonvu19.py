# viewer.py
import curses
import json
import sys
import re
from pathlib import Path
from collections import deque
import textwrap

def format_record(record, max_width=80, highlight_terms=None):
    """Format the full record into lines for display."""
    highlight_terms = highlight_terms or []
    lines = []

    def add_field(name, value):
        if value is None:
            return
        if isinstance(value, list) and not isinstance(value, str):
            if value and isinstance(value[0], dict):
                lines.append(f"{name}: [")
                for item in value:
                    for k, v in item.items():
                        line = f"    {k}: {v}"
                        if any(term.lower() in line.lower() for term in highlight_terms):
                            line = "  " + line
                        lines.append(line)
                lines.append("]")
            elif any(value):
                line = f"{name}: {', '.join(map(str, value))}"
                if any(term.lower() in line.lower() for term in highlight_terms):
                    line = "  " + line
                lines.append(line)
        else:
            line = f"{name}: {value}"
            if any(term.lower() in line.lower() for term in highlight_terms):
                line = "  " + line
            lines.append(line)

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
            if any(term.lower() in line.lower() for term in highlight_terms):
                line = "    " + line
            lines.append(line)

    ner = record.get("ner")
    if ner:
        lines.append("NER:")
        for sentence_data in ner:
            sentence = sentence_data.get("sentence", "")
            spans = sentence_data.get("spans", [])
            line = f"    Sentence: {sentence[:max_width - 12]}"
            if any(term.lower() in line.lower() for term in highlight_terms):
                line = "    " + line
            lines.append(line)
            for span in spans:
                span_text = span.get("text", "")
                span_value = span.get("value", "")
                if span_text and span_value:
                    line = f"        Span: {span_text} -> {span_value}"
                    if any(term.lower() in line.lower() for term in highlight_terms):
                        line = "    " + line
                    lines.append(line)

    return lines


def main(stdscr, file_path):
    # Initialize curses
    curses.curs_set(0)
    stdscr.timeout(100)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Highlight
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLUE)    # Filtered tag
    max_y, max_x = stdscr.getmaxyx()
    display_height = max_y - 3
    display_win = stdscr.subwin(display_height, max_x, 0, 0)
    search_win = stdscr.subwin(1, max_x, display_height, 0)
    status_win = stdscr.subwin(1, max_x, display_height + 1, 0)

    # Load data
    records = []
    source_to_records = {}
    current_index = 0
    current_source_index = 0
    scroll_offset = 0
    search_results = []
    is_searching = False
    search_query = ""
    filter_ner_tag = None
    filter_span_text = None

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
    for source in sources:
        source_to_records[source] = [
            i for i, r in enumerate(records) if r.get("source") == source
        ]

    # Precompute and cache all unique span texts from NER
    cached_span_texts = set()
    for record in records:
        for sentence_data in record.get("ner", []):
            for span in sentence_data.get("spans", []):
                cached_span_texts.add(span.get("text"))
    span_list = sorted(cached_span_texts)

    def get_displayed_records():
        nonlocal search_results, records, filter_ner_tag, filter_span_text
        candidates = search_results if is_searching else records

        filtered = []

        for r in candidates:
            ner_filtered = True
            if filter_ner_tag:
                ner_filtered = any(
                    any(span["value"] == filter_ner_tag for span in sent.get("spans", []))
                    for sent in r.get("ner", [])
                )

            span_filtered = True
            if filter_span_text:
                span_filtered = any(
                    any(span["text"] == filter_span_text for span in sent.get("spans", []))
                    for sent in r.get("ner", [])
                )

            if ner_filtered and span_filtered:
                filtered.append(r)

        return filtered

    def show_entity_popup():
        """Show a scrollable popup listing all unique NER entity texts."""
        if not span_list:
            return None

        popup_height = min(len(span_list) + 2, max_y - 4)
        popup_width = min(60, max_x - 4)
        start_y = (max_y - popup_height) // 2
        start_x = (max_x - popup_width) // 2
        popup_win = curses.newwin(popup_height, popup_width, start_y, start_x)
        popup_win.bkgd(' ', curses.color_pair(4))
        popup_win.border()

        title = " Select NER Text "
        popup_win.addstr(0, (popup_width - len(title)) // 2, title, curses.color_pair(5))

        choice = 0
        scroll_pos = 0

        while True:
            visible_items = popup_height - 2
            popup_win.clear()
            popup_win.border()
            popup_win.addstr(0, (popup_width - len(title)) // 2, title, curses.color_pair(5))

            for idx in range(min(visible_items, len(span_list))):
                global_idx = idx + scroll_pos
                if global_idx >= len(span_list):
                    break
                text = span_list[global_idx]
                attr = curses.A_REVERSE if idx == choice else curses.A_NORMAL
                popup_win.addstr(idx + 1, 2, f" {text.ljust(popup_width - 6)} ", attr)

            popup_win.refresh()
            key = stdscr.getch()

            if key == curses.KEY_UP:
                if choice > 0:
                    choice -= 1
                elif scroll_pos > 0:
                    scroll_pos -= 1
            elif key == curses.KEY_DOWN:
                if choice < visible_items - 1 and scroll_pos + choice < len(span_list) - 1:
                    choice += 1
                elif scroll_pos + visible_items < len(span_list):
                    scroll_pos += 1
            elif key == 10:  # Enter
                return span_list[choice + scroll_pos]
            elif key == 27 or key == ord('q'):  # Escape or q to cancel
                return None

    def update_display():
        nonlocal scroll_offset
        display_win.clear()
        displayed_records = get_displayed_records()
        if not displayed_records:
            display_win.addstr(0, 0, "No records found.", curses.color_pair(1))
        else:
            record = displayed_records[current_index % len(displayed_records)]
            lines = format_record(record, max_x - 4, [search_query] if search_query else [])
            scroll_offset = min(scroll_offset, max(0, len(lines) - display_height))
            for i in range(display_height):
                real_line_idx = i + scroll_offset
                if real_line_idx >= len(lines):
                    break
                line = lines[real_line_idx][:max_x - 1]
                attr = curses.A_NORMAL
                if any(term.lower() in line.lower() for term in ([search_query] if search_query else [])):
                    attr |= curses.color_pair(4)
                display_win.addstr(i, 0, line, attr)
        display_win.noutrefresh()

    def update_status(message=None):
        nonlocal last_status_message
        last_status_message = message
        status_win.clear()
        match_count = len(get_displayed_records())
        total_count = len(records)
        parts = []
        if filter_ner_tag:
            parts.append(f"NER Tag: {filter_ner_tag} | ")
        if filter_span_text:
            parts.append(f"NER Text: {filter_span_text} | ")
        parts.append(f"{match_count} matches / {total_count} total | ")
        parts.append("↑↓: Sources | ←→: Navigate | PageUp/Down: Scroll | F: Toggle NER Filter | E: Select Entity Text | Esc: Clear Filters | q: Quit")
        text = "".join(parts)
        status_win.addstr(0, 0, text[:max_x - 1], curses.color_pair(3))
        status_win.noutrefresh()

    def update_search():
        search_win.clear()
        search_win.addstr(0, 0, "Search: " + search_query[:max_x - 8], curses.color_pair(2))
        search_win.noutrefresh()

    def export_records():
        fname = "exported_records.jsonl"
        with open(fname, "w", encoding="utf-8") as f:
            for record in get_displayed_records():
                f.write(json.dumps(record) + "\n")
        return fname

    update_display()
    update_search()
    update_status()
    curses.doupdate()

    while True:
        key = stdscr.getch()
        if key == -1:
            continue

        displayed_records = get_displayed_records()

        if key == ord("q"):
            break

        elif key == ord("f") or key == ord("F"):
            if not filter_ner_tag:
                filter_ner_tag = "PERSON"
            else:
                ner_tags = ["PERSON", "GPE", "ORG", "DATE", "PERCENT"]
                idx = (ner_tags.index(filter_ner_tag) + 1) % len(ner_tags)
                filter_ner_tag = ner_tags[idx]
            current_index = 0
            scroll_offset = 0
            update_display()
            update_status()

        elif key == ord("e") or key == ord("E"):
            selected_span_text = show_entity_popup()
            if selected_span_text:
                filter_span_text = selected_span_text
                current_index = 0
                scroll_offset = 0
                update_display()
                update_status(f"Filtering by NER text: {selected_span_text}")

        elif key == curses.KEY_UP:
            if sources:
                current_source_index = (current_source_index - 1) % len(sources)
                selected_source = sources[current_source_index]
                is_searching = True
                search_results = [records[i] for i in source_to_records[selected_source]]
                current_index = 0
                scroll_offset = 0
                update_display()
                update_status()

        elif key == curses.KEY_DOWN:
            if sources:
                current_source_index = (current_source_index + 1) % len(sources)
                selected_source = sources[current_source_index]
                is_searching = True
                search_results = [records[i] for i in source_to_records[selected_source]]
                current_index = 0
                scroll_offset = 0
                update_display()
                update_status()

        elif key == curses.KEY_LEFT:
            if displayed_records:
                current_index = (current_index - 1) % len(displayed_records)
                scroll_offset = 0
                update_display()
                update_status()

        elif key == curses.KEY_RIGHT:
            if displayed_records:
                current_index = (current_index + 1) % len(displayed_records)
                scroll_offset = 0
                update_display()
                update_status()

        elif key == curses.KEY_NPAGE:
            if displayed_records:
                scroll_offset = min(scroll_offset + 1, max(0, len(format_record(displayed_records[current_index])) - display_height))
                update_display()

        elif key == curses.KEY_PPAGE:
            scroll_offset = max(scroll_offset - 1, 0)
            update_display()

        elif key == 10:  # Enter to search
            query = search_query.strip().lower()
            if query:
                is_searching = True
                scroll_offset = 0
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
            update_status()

        elif key == 27:  # Escape
            is_searching = False
            search_results = []
            search_query = ""
            filter_ner_tag = None
            filter_span_text = None
            current_index = 0
            scroll_offset = 0
            update_display()
            update_search()
            update_status()

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
