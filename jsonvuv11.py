import curses
import json
import os
import argparse
from collections import defaultdict
from typing import List, Dict, Any, Set

class JsonViewer:
    def __init__(self, stdscr, filename: str):
        self.stdscr = stdscr
        self.filename = filename
        self.data: List[Dict[str, Any]] = []
        self.summary: Dict[str, Set[str]] = defaultdict(set)
        self.selected_ids: Set[Any] = set()
        self.current_page = 0
        self.items_per_page = 0
        self.mode = 'summary'  # 'summary', 'list', 'search', 'edit', 'search_input', 'export'
        self.search_field = ''
        self.search_value = ''
        self.filtered_data: List[Dict[str, Any]] = []
        self.cursor_pos = 0
        self.current_record_id = None  # Tracks current record ID in list/search
        self.current_field_index = 0  # Tracks current field in list/search/export
        self.all_fields: List[str] = []
        self.selected_fields: Set[str] = set()  # For export
        self.current_export_record: Dict[str, Any] = {}
        self.current_export_index = 0  # Index in sorted selected_ids for export/edit
        self.selected_summary_fields: Set[str] = set()  # For summary mode
        self.sorted_ids: List[Any] = []  # Sorted list of all record IDs
        self.load_data()
        self.load_summary()
        self.setup_curses()

    def load_data(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"File {self.filename} not found")
        self.data = []
        with open(self.filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        item = json.loads(line)
                        if 'id' not in item:
                            raise ValueError("Each JSON object must have an 'id' field")
                        self.data.append(item)
                        self.all_fields.extend([k for k in item.keys() if k not in self.all_fields])
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON line: {line}\n{e}")
                        raise
        self.all_fields = sorted(list(set(self.all_fields)))
        self.sorted_ids = sorted([item['id'] for item in self.data])
        if not self.data:
            raise ValueError("Input file is empty or contains no valid JSON records")
        self.current_record_id = self.sorted_ids[0] if self.sorted_ids else None

    def load_summary(self):
        self.summary = defaultdict(set)
        target_data = [item for item in self.data if item['id'] in self.selected_ids] if self.selected_ids else self.data
        for item in target_data:
            for key, value in item.items():
                self.summary[key].add(str(value))

    def setup_curses(self):
        curses.curs_set(0)
        self.stdscr.timeout(100)
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self.calculate_items_per_page()

    def calculate_items_per_page(self):
        max_y, _ = self.stdscr.getmaxyx()
        self.items_per_page = max_y - 5  # Reserve lines for menu, header, status

    def draw_menu(self):
        menu_items = [
            "S:Summary", "L:List", "F:Search", "E:Edit Selections",
            "X:Export", "Q:Quit", f"Selected: {len(self.selected_ids)}"
        ]
        menu_str = " | ".join(menu_items)
        self.stdscr.addnstr(0, 0, menu_str, curses.COLS, curses.color_pair(2))

    def draw_summary(self):
        self.stdscr.clear()
        self.draw_menu()
        row = 2
        max_y, max_x = self.stdscr.getmaxyx()
        keys = list(self.summary.keys())
        start = self.current_page * self.items_per_page
        end = min(start + self.items_per_page, len(keys))
        for idx, key in enumerate(keys[start:end], start):
            if row >= max_y - 2:
                break
            selected = key in self.selected_summary_fields
            prefix = "* " if selected else "  "
            values = sorted(self.summary[key])
            value_str = ", ".join(values[:max_x//4])
            if len(values) > max_x//4:
                value_str += "..."
            attrs = curses.color_pair(1) if idx - start == self.cursor_pos else 0
            self.stdscr.addnstr(row, 0, f"{prefix}{key}: {value_str}", max_x - 1, attrs)
            row += 1
        status = f"Page {self.current_page + 1}/{(len(keys) + self.items_per_page - 1)//self.items_per_page}"
        self.stdscr.addstr(max_y - 2, 0, f"Showing summary of {'selected records (' + str(len(self.selected_ids)) + ')' if self.selected_ids else 'all records'}")
        self.stdscr.addstr(max_y - 1, 0, f"Up/Down: Navigate Field | Space: Toggle Select | Right/Left: Change page | {status}")

    def draw_list(self):
        self.stdscr.clear()
        self.draw_menu()
        row = 2
        max_y, max_x = self.stdscr.getmaxyx()
        data = self.filtered_data if self.mode == 'search' else self.data
        if not data:
            self.stdscr.addstr(row, 0, "No records to display")
            self.stdscr.addstr(max_y - 1, 0, "Esc: Back")
            return
        current_record = next((item for item in data if item['id'] == self.current_record_id), data[0])
        selected = current_record['id'] in self.selected_ids
        self.stdscr.addstr(row, 0, f"Record ID: {current_record['id']} {'(Selected)' if selected else ''}")
        row += 1
        fields = sorted(current_record.keys())
        for idx, field in enumerate(fields):
            if row >= max_y - 2:
                break
            prefix = "* " if idx == self.current_field_index else "  "
            item_str = f"{prefix}{field}: {str(current_record[field])[:max_x-10]}"
            attrs = curses.color_pair(1) if idx == self.current_field_index else 0
            self.stdscr.addnstr(row, 0, item_str, max_x - 1, attrs)
            row += 1
        status = f"Record ID {self.current_record_id}/{self.sorted_ids[-1] if self.sorted_ids else 'N/A'}"
        self.stdscr.addstr(max_y - 1, 0, f"Up/Down: Navigate Field | Space: Toggle Record | Right/Left: Prev/Next ID | {status}")

    def draw_search(self):
        self.stdscr.clear()
        self.draw_menu()
        max_y, max_x = self.stdscr.getmaxyx()
        box_width = max_x - 4
        self.stdscr.addstr(max_y - 3, 0, "-" * box_width, curses.color_pair(3))
        prompt = f"Field: {self.search_field} | Value: {self.search_value}"
        self.stdscr.addnstr(max_y - 2, 0, prompt[:box_width-1], box_width-1, curses.color_pair(3))
        self.stdscr.addstr(max_y - 1, 0, "-" * box_width, curses.color_pair(3))
        curses.curs_set(1)
        self.stdscr.move(max_y - 2, min(len(prompt) + 1, box_width - 1))

    def draw_edit(self):
        self.stdscr.clear()
        self.draw_menu()
        row = 2
        max_y, max_x = self.stdscr.getmaxyx()
        selected_list = sorted(self.selected_ids)
        if not selected_list:
            self.stdscr.addstr(row, 0, "No selected records")
            self.stdscr.addstr(max_y - 1, 0, "Esc: Back")
            return
        current_id = selected_list[self.current_export_index]
        self.stdscr.addstr(row, 0, f"Selected ID: {current_id}")
        row += 1
        start = self.current_page * self.items_per_page
        end = min(start + self.items_per_page, len(selected_list))
        for idx, id_ in enumerate(selected_list[start:end], start):
            if row >= max_y - 2:
                break
            attrs = curses.color_pair(1) if id_ == current_id else 0
            self.stdscr.addnstr(row, 0, f"ID: {id_}", max_x - 1, attrs)
            row += 1
        status = f"ID {current_id}/{selected_list[-1] if selected_list else 'N/A'}"
        self.stdscr.addstr(max_y - 1, 0, f"Up/Down: Navigate ID | Space: Toggle Remove | C: Clear All | Right/Left: Prev/Next ID | {status}")

    def draw_export(self):
        self.stdscr.clear()
        self.draw_menu()
        row = 2
        max_y, max_x = self.stdscr.getmaxyx()
        if not self.current_export_record:
            self.stdscr.addstr(row, 0, "No selected records to export")
            self.stdscr.addstr(max_y - 1, 0, "Esc: Cancel")
            return
        self.stdscr.addstr(row, 0, f"Exporting fields for record ID: {self.current_export_record['id']} ({self.current_export_index + 1}/{len(self.selected_ids)})")
        row += 1
        fields = sorted(self.current_export_record.keys())
        for idx, field in enumerate(fields):
            if row >= max_y - 2:
                break
            selected = field in self.selected_fields
            prefix = "* " if selected else "  "
            item_str = f"{prefix}{field}: {str(self.current_export_record[field])[:max_x-10]}"
            attrs = curses.color_pair(1) if idx == self.current_field_index else 0
            self.stdscr.addnstr(row, 0, item_str, max_x - 1, attrs)
            row += 1
        self.stdscr.addstr(max_y - 1, 0, f"Up/Down: Navigate Field | Space: Toggle Select | Enter: Export | Esc: Cancel | Right/Left: Prev/Next ID")

    def export_selected(self):
        if not self.selected_ids or not self.selected_fields:
            return
        export_data = []
        for item in self.data:
            if item['id'] in self.selected_ids:
                export_item = {k: item.get(k) for k in self.selected_fields if k in item}
                export_data.append(export_item)
        with open('export.json', 'w') as f:
            json.dump(export_data, f, indent=2)

    def find_next_id(self, current_id: Any, ids: List[Any]) -> Any:
        try:
            idx = ids.index(current_id)
            return ids[idx + 1] if idx + 1 < len(ids) else current_id
        except ValueError:
            return current_id

    def find_prev_id(self, current_id: Any, ids: List[Any]) -> Any:
        try:
            idx = ids.index(current_id)
            return ids[idx - 1] if idx > 0 else current_id
        except ValueError:
            return current_id

    def handle_input(self):
        try:
            key = self.stdscr.getch()
            if key == -1:
                return
            if self.mode == 'summary':
                self.handle_summary_input(key)
            elif self.mode in ['list', 'search']:
                self.handle_list_input(key)
            elif self.mode == 'edit':
                self.handle_edit_input(key)
            elif self.mode == 'search_input':
                self.handle_search_input(key)
            elif self.mode == 'export':
                self.handle_export_input(key)
        except curses.error as e:
            self.stdscr.addstr(1, 0, f"Error: {str(e)}  ")

    def handle_summary_input(self, key):
        max_pages = (len(self.summary) + self.items_per_page - 1) // self.items_per_page
        keys = list(self.summary.keys())
        if key == curses.KEY_UP:
            self.cursor_pos = max(0, self.cursor_pos - 1)
            if self.cursor_pos < 0 and self.current_page > 0:
                self.current_page -= 1
                self.cursor_pos = self.items_per_page - 1
        elif key == curses.KEY_DOWN:
            self.cursor_pos = min(self.items_per_page - 1, self.cursor_pos + 1)
            if self.cursor_pos >= min(self.items_per_page, len(keys) - self.current_page * self.items_per_page) and self.current_page < max_pages - 1:
                self.current_page += 1
                self.cursor_pos = 0
        elif key == curses.KEY_LEFT and self.current_page > 0:
            self.current_page -= 1
            self.cursor_pos = 0
        elif key == curses.KEY_RIGHT and self.current_page < max_pages - 1:
            self.current_page += 1
            self.cursor_pos = 0
        elif key == ord(' '):
            index = self.current_page * self.items_per_page + self.cursor_pos
            if 0 <= index < len(keys):
                field = keys[index]
                if field in self.selected_summary_fields:
                    self.selected_summary_fields.remove(field)
                else:
                    self.selected_summary_fields.add(field)
        elif key in (ord('s'), ord('S')):
            self.mode = 'summary'
            self.current_page = 0
            self.cursor_pos = 0
        elif key in (ord('l'), ord('L')):
            self.mode = 'list'
            self.current_record_id = self.sorted_ids[0] if self.sorted_ids else None
            self.current_field_index = 0
        elif key in (ord('f'), ord('F')):
            self.mode = 'search_input'
            self.search_field = ''
            self.search_value = ''
        elif key in (ord('e'), ord('E')):
            self.mode = 'edit'
            self.current_page = 0
            self.current_export_index = 0
            self.cursor_pos = 0
        elif key in (ord('x'), ord('X')):
            self.mode = 'export'
            self.current_field_index = 0
            self.current_export_index = 0
            self.selected_fields = set()
            selected_list = sorted(self.selected_ids)
            self.current_export_record = next((item for item in self.data if item['id'] == selected_list[self.current_export_index]), {}) if selected_list else {}
        elif key in (ord('q'), ord('Q')):
            raise SystemExit

    def handle_list_input(self, key):
        data = self.filtered_data if self.mode == 'search' else self.data
        if not data:
            if key == 27:  # Esc
                self.mode = 'list'
                self.current_record_id = self.sorted_ids[0] if self.sorted_ids else None
                self.current_field_index = 0
            return
        current_record = next((item for item in data if item['id'] == self.current_record_id), data[0])
        fields = sorted(current_record.keys())
        valid_ids = sorted([item['id'] for item in data])
        if key == curses.KEY_UP:
            self.current_field_index = max(0, self.current_field_index - 1)
        elif key == curses.KEY_DOWN:
            self.current_field_index = min(len(fields) - 1, self.current_field_index + 1)
        elif key == curses.KEY_LEFT:
            self.current_record_id = self.find_prev_id(self.current_record_id, valid_ids)
            self.current_field_index = 0
        elif key == curses.KEY_RIGHT:
            self.current_record_id = self.find_next_id(self.current_record_id, valid_ids)
            self.current_field_index = 0
        elif key == ord(' '):
            item_id = current_record['id']
            if item_id in self.selected_ids:
                self.selected_ids.remove(item_id)
            else:
                self.selected_ids.add(item_id)
            self.load_summary()
        elif key in (ord('s'), ord('S')):
            self.mode = 'summary'
            self.current_page = 0
            self.cursor_pos = 0
        elif key in (ord('l'), ord('L')):
            self.mode = 'list'
            self.current_record_id = valid_ids[0] if valid_ids else None
            self.current_field_index = 0
        elif key in (ord('f'), ord('F')):
            self.mode = 'search_input'
            self.search_field = ''
            self.search_value = ''
        elif key in (ord('e'), ord('E')):
            self.mode = 'edit'
            self.current_page = 0
            self.current_export_index = 0
            self.cursor_pos = 0
        elif key in (ord('x'), ord('X')):
            self.mode = 'export'
            self.current_field_index = 0
            self.current_export_index = 0
            self.selected_fields = set()
            selected_list = sorted(self.selected_ids)
            self.current_export_record = next((item for item in self.data if item['id'] == selected_list[self.current_export_index]), {}) if selected_list else {}
        elif key in (ord('q'), ord('Q')):
            raise SystemExit

    def handle_search_input(self, key):
        if key == 27:  # Esc
            self.mode = 'list'
            self.current_record_id = self.sorted_ids[0] if self.sorted_ids else None
            self.current_field_index = 0
            curses.curs_set(0)
        elif key == curses.KEY_BACKSPACE:
            if self.search_value:
                self.search_value = self.search_value[:-1]
            elif self.search_field:
                self.search_field = self.search_field[:-1]
        elif key == 10:  # Enter
            if self.search_field and self.search_value:
                self.filtered_data = [
                    item for item in self.data
                    if self.search_field in item and str(item[self.search_field]).lower().find(self.search_value.lower()) != -1
                ]
                self.mode = 'search'
                self.current_record_id = sorted([item['id'] for item in self.filtered_data])[0] if self.filtered_data else None
                self.current_field_index = 0
            else:
                self.mode = 'list'
                self.current_record_id = self.sorted_ids[0] if self.sorted_ids else None
            curses.curs_set(0)
        elif 32 <= key <= 126:  # Printable characters
            if len(self.search_field) < 20 and not self.search_value:
                self.search_field += chr(key)
            elif len(self.search_value) < 20:
                self.search_value += chr(key)

    def handle_edit_input(self, key):
        selected_list = sorted(self.selected_ids)
        if not selected_list:
            if key == 27:  # Esc
                self.mode = 'list'
                self.current_record_id = self.sorted_ids[0] if self.sorted_ids else None
                self.current_field_index = 0
            return
        max_pages = (len(selected_list) + self.items_per_page - 1) // self.items_per_page
        if key == curses.KEY_UP:
            self.cursor_pos = max(0, self.cursor_pos - 1)
            if self.cursor_pos < 0 and self.current_page > 0:
                self.current_page -= 1
                self.cursor_pos = self.items_per_page - 1
        elif key == curses.KEY_DOWN:
            self.cursor_pos = min(self.items_per_page - 1, self.cursor_pos + 1)
            if self.cursor_pos >= min(self.items_per_page, len(selected_list) - self.current_page * self.items_per_page) and self.current_page < max_pages - 1:
                self.current_page += 1
                self.cursor_pos = 0
        elif key == curses.KEY_LEFT:
            self.current_export_index = max(0, self.current_export_index - 1)
            self.current_page = self.current_export_index // self.items_per_page
            self.cursor_pos = self.current_export_index % self.items_per_page
        elif key == curses.KEY_RIGHT:
            self.current_export_index = min(len(selected_list) - 1, self.current_export_index + 1)
            self.current_page = self.current_export_index // self.items_per_page
            self.cursor_pos = self.current_export_index % self.items_per_page
        elif key == ord(' '):
            index = self.current_page * self.items_per_page + self.cursor_pos
            if 0 <= index < len(selected_list):
                self.selected_ids.remove(selected_list[index])
                self.load_summary()
                if index >= len(selected_list) - 1:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                    self.current_export_index = max(0, self.current_export_index - 1)
        elif key in (ord('c'), ord('C')):
            self.selected_ids.clear()
            self.load_summary()
        elif key == 27:  # Esc
            self.mode = 'list'
            self.current_record_id = self.sorted_ids[0] if self.sorted_ids else None
            self.current_field_index = 0
        elif key in (ord('s'), ord('S')):
            self.mode = 'summary'
            self.current_page = 0
            self.cursor_pos = 0
        elif key in (ord('l'), ord('L')):
            self.mode = 'list'
            self.current_record_id = self.sorted_ids[0] if self.sorted_ids else None
            self.current_field_index = 0
        elif key in (ord('f'), ord('F')):
            self.mode = 'search_input'
            self.search_field = ''
            self.search_value = ''
        elif key in (ord('x'), ord('X')):
            self.mode = 'export'
            self.current_field_index = 0
            self.current_export_index = 0
            self.selected_fields = set()
            selected_list = sorted(self.selected_ids)
            self.current_export_record = next((item for item in self.data if item['id'] == selected_list[self.current_export_index]), {}) if selected_list else {}
        elif key in (ord('q'), ord('Q')):
            raise SystemExit

    def handle_export_input(self, key):
        if not self.current_export_record:
            if key == 27:  # Esc
                self.mode = 'list'
                self.current_record_id = self.sorted_ids[0] if self.sorted_ids else None
                self.current_field_index = 0
            return
        fields = sorted(self.current_export_record.keys())
        selected_list = sorted(self.selected_ids)
        if key == curses.KEY_UP:
            self.current_field_index = max(0, self.current_field_index - 1)
        elif key == curses.KEY_DOWN:
            self.current_field_index = min(len(fields) - 1, self.current_field_index + 1)
        elif key == curses.KEY_LEFT:
            self.current_export_index = max(0, self.current_export_index - 1)
            self.current_export_record = next((item for item in self.data if item['id'] == selected_list[self.current_export_index]), {})
            self.current_field_index = 0
        elif key == curses.KEY_RIGHT:
            self.current_export_index = min(len(selected_list) - 1, self.current_export_index + 1)
            self.current_export_record = next((item for item in self.data if item['id'] == selected_list[self.current_export_index]), {})
            self.current_field_index = 0
        elif key == ord(' '):
            if 0 <= self.current_field_index < len(fields):
                field = fields[self.current_field_index]
                if field in self.selected_fields:
                    self.selected_fields.remove(field)
                else:
                    self.selected_fields.add(field)
        elif key == 10:  # Enter
            self.export_selected()
            self.mode = 'list'
            self.current_record_id = self.sorted_ids[0] if self.sorted_ids else None
            self.current_field_index = 0
        elif key == 27:  # Esc
            self.mode = 'list'
            self.current_record_id = self.sorted_ids[0] if self.sorted_ids else None
            self.current_field_index = 0
        elif key in (ord('s'), ord('S')):
            self.mode = 'summary'
            self.current_page = 0
            self.cursor_pos = 0
        elif key in (ord('l'), ord('L')):
            self.mode = 'list'
            self.current_record_id = self.sorted_ids[0] if self.sorted_ids else None
            self.current_field_index = 0
        elif key in (ord('f'), ord('F')):
            self.mode = 'search_input'
            self.search_field = ''
            self.search_value = ''
        elif key in (ord('q'), ord('Q')):
            raise SystemExit

    def run(self):
        while True:
            if self.mode == 'summary':
                self.draw_summary()
            elif self.mode in ['list', 'search']:
                self.draw_list()
            elif self.mode == 'edit':
                self.draw_edit()
            elif self.mode == 'search_input':
                self.draw_search()
            elif self.mode == 'export':
                self.draw_export()
            self.stdscr.refresh()
            self.handle_input()

def main(stdscr):
    parser = argparse.ArgumentParser(description="JSON Viewer for JSON Lines files")
    parser.add_argument("filename", help="Path to the JSON Lines input file")
    args = parser.parse_args()
    
    if not os.path.exists(args.filename):
        print(f"Error: File '{args.filename}' does not exist")
        return
    
    app = JsonViewer(stdscr, args.filename)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
