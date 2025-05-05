import curses
import json
import os
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
        self.all_fields: List[str] = []
        self.selected_fields: Set[str] = set()
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
        if not self.data:
            raise ValueError("Input file is empty or contains no valid JSON records")

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
        self.items_per_page = max_y - 5  # Reserve lines for menu, header, status, search/export box

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
        end = start + self.items_per_page
        for key in keys[start:end]:
            if row >= max_y - 2:
                break
            values = sorted(self.summary[key])
            value_str = ", ".join(values[:max_x//4])
            if len(values) > max_x//4:
                value_str += "..."
            self.stdscr.addnstr(row, 0, f"{key}: {value_str}", max_x - 1)
            row += 1
        status = f"Showing summary of {'selected records (' + str(len(self.selected_ids)) + ')' if self.selected_ids else 'all records'}"
        self.stdscr.addstr(max_y - 2, 0, status)
        self.stdscr.addstr(max_y - 1, 0, "Arrows: Navigate | Space: N/A | PageUp/Down: Change page")

    def draw_list(self):
        self.stdscr.clear()
        self.draw_menu()
        row = 2
        max_y, max_x = self.stdscr.getmaxyx()
        data = self.filtered_data if self.mode == 'search' else self.data
        start = self.current_page * self.items_per_page
        end = min(start + self.items_per_page, len(data))
        for idx, item in enumerate(data[start:end], start):
            if row >= max_y - 2:
                break
            selected = item['id'] in self.selected_ids
            prefix = "* " if selected else "  "
            item_str = f"{prefix}{item['id']}: {str(item)[:max_x-10]}"
            attrs = curses.color_pair(1) if idx - start == self.cursor_pos else 0
            self.stdscr.addnstr(row, 0, item_str, max_x - 1, attrs)
            row += 1
        status = f"Page {self.current_page + 1}/{(len(data) + self.items_per_page - 1)//self.items_per_page}"
        self.stdscr.addstr(max_y - 1, 0, "Arrows: Navigate | Space: Select | PageUp/Down: Change page | " + status)

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

    def draw_export(self):
        self.stdscr.clear()
        self.draw_menu()
        row = 2
        max_y, max_x = self.stdscr.getmaxyx()
        start = self.current_page * self.items_per_page
        end = min(start + self.items_per_page, len(self.all_fields))
        for idx, field in enumerate(self.all_fields[start:end], start):
            if row >= max_y - 2:
                break
            selected = field in self.selected_fields
            prefix = "* " if selected else "  "
            item_str = f"{prefix}{field}"
            attrs = curses.color_pair(1) if idx - start == self.cursor_pos else 0
            self.stdscr.addnstr(row, 0, item_str, max_x - 1, attrs)
            row += 1
        status = f"Page {self.current_page + 1}/{(len(self.all_fields) + self.items_per_page - 1)//self.items_per_page}"
        self.stdscr.addstr(max_y - 1, 0, "Space: Toggle Field | Enter: Export | Esc: Cancel | " + status)

    def export_selected(self):
        if not self.selected_ids or not self.selected_fields:
            return
        export_data = []
        for item in self.data:
            if item['id'] in self.selected_ids:
                export_item = {k: item.get(k) for k in self.selected_fields}
                export_data.append(export_item)
        with open('export.json', 'w') as f:
            json.dump(export_data, f, indent=2)

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
        except curses.error:
            pass

    def handle_summary_input(self, key):
        max_pages = (len(self.summary) + self.items_per_page - 1) // self.items_per_page
        if key == curses.KEY_UP:
            self.current_page = max(0, self.current_page - 1)
        elif key == curses.KEY_DOWN or key == curses.KEY_NPAGE:
            self.current_page = min(max_pages - 1, self.current_page + 1)
        elif key == curses.KEY_PPAGE:
            self.current_page = max(0, self.current_page - 1)
        elif key in (ord('s'), ord('S')):
            self.mode = 'summary'
            self.current_page = 0
        elif key in (ord('l'), ord('L')):
            self.mode = 'list'
            self.current_page = 0
            self.cursor_pos = 0
        elif key in (ord('f'), ord('F')):
            self.mode = 'search_input'
            self.search_field = ''
            self.search_value = ''
        elif key in (ord('e'), ord('E')):
            self.mode = 'edit'
            self.current_page = 0
            self.cursor_pos = 0
        elif key in (ord('x'), ord('X')):
            self.mode = 'export'
            self.current_page = 0
            self.cursor_pos = 0
            self.selected_fields = set()
        elif key in (ord('q'), ord('Q')):
            raise SystemExit

    def handle_list_input(self, key):
        data = self.filtered_data if self.mode == 'search' else self.data
        max_pages = (len(data) + self.items_per_page - 1) // self.items_per_page
        if key == curses.KEY_UP:
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif key == curses.KEY_DOWN:
            self.cursor_pos = min(self.items_per_page - 1, self.cursor_pos + 1)
        elif key == curses.KEY_NPAGE:
            self.current_page = min(max_pages - 1, self.current_page + 1)
            self.cursor_pos = 0
        elif key == curses.KEY_PPAGE:
            self.current_page = max(0, self.current_page - 1)
            self.cursor_pos = 0
        elif key == ord(' '):
            index = self.current_page * self.items_per_page + self.cursor_pos
            if 0 <= index < len(data):
                item_id = data[index]['id']
                if item_id in self.selected_ids:
                    self.selected_ids.remove(item_id)
                else:
                    self.selected_ids.add(item_id)
                self.load_summary()
        elif key in (ord('s'), ord('S')):
            self.mode = 'summary'
            self.current_page = 0
        elif key in (ord('l'), ord('L')):
            self.mode = 'list'
            self.current_page = 0
            self.cursor_pos = 0
        elif key in (ord('f'), ord('F')):
            self.mode = 'search_input'
            self.search_field = ''
            self.search_value = ''
        elif key in (ord('e'), ord('E')):
            self.mode = 'edit'
            self.current_page = 0
            self.cursor_pos = 0
        elif key in (ord('x'), ord('X')):
            self.mode = 'export'
            self.current_page = 0
            self.cursor_pos = 0
            self.selected_fields = set()
        elif key in (ord('q'), ord('Q')):
            raise SystemExit

    def handle_search_input(self, key):
        if key == 27:  # Esc
            self.mode = 'list'
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
                self.current_page = 0
                self.cursor_pos = 0
            else:
                self.mode = 'list'
            curses.curs_set(0)
        elif 32 <= key <= 126:  # Printable characters
            if len(self.search_field) < 20 and not self.search_value:
                self.search_field += chr(key)
            elif len(self.search_value) < 20:
                self.search_value += chr(key)

    def handle_edit_input(self, key):
        max_pages = (len(self.selected_ids) + self.items_per_page - 1) // self.items_per_page
        if key == curses.KEY_UP:
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif key == curses.KEY_DOWN:
            self.cursor_pos = min(self.items_per_page - 1, self.cursor_pos + 1)
        elif key == curses.KEY_NPAGE:
            self.current_page = min(max_pages - 1, self.current_page + 1)
            self.cursor_pos = 0
        elif key == curses.KEY_PPAGE:
            self.current_page = max(0, self.current_page - 1)
            self.cursor_pos = 0
        elif key == ord(' '):
            index = self.current_page * self.items_per_page + self.cursor_pos
            selected_list = sorted(self.selected_ids)
            if 0 <= index < len(selected_list):
                self.selected_ids.remove(selected_list[index])
                self.load_summary()
        elif key in (ord('c'), ord('C')):
            self.selected_ids.clear()
            self.load_summary()
        elif key == 27:  # Esc
            self.mode = 'list'
            self.current_page = 0
            self.cursor_pos = 0
        elif key in (ord('s'), ord('S')):
            self.mode = 'summary'
            self.current_page = 0
        elif key in (ord('l'), ord('L')):
            self.mode = 'list'
            self.current_page = 0
            self.cursor_pos = 0
        elif key in (ord('f'), ord('F')):
            self.mode = 'search_input'
            self.search_field = ''
            self.search_value = ''
        elif key in (ord('x'), ord('X')):
            self.mode = 'export'
            self.current_page = 0
            self.cursor_pos = 0
            self.selected_fields = set()
        elif key in (ord('q'), ord('Q')):
            raise SystemExit

    def handle_export_input(self, key):
        max_pages = (len(self.all_fields) + self.items_per_page - 1) // self.items_per_page
        if key == curses.KEY_UP:
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif key == curses.KEY_DOWN:
            self.cursor_pos = min(self.items_per_page - 1, self.cursor_pos + 1)
        elif key == curses.KEY_NPAGE:
            self.current_page = min(max_pages - 1, self.current_page + 1)
            self.cursor_pos = 0
        elif key == curses.KEY_PPAGE:
            self.current_page = max(0, self.current_page - 1)
            self.cursor_pos = 0
        elif key == ord(' '):
            index = self.current_page * self.items_per_page + self.cursor_pos
            if 0 <= index < len(self.all_fields):
                field = self.all_fields[index]
                if field in self.selected_fields:
                    self.selected_fields.remove(field)
                else:
                    self.selected_fields.add(field)
        elif key == 10:  # Enter
            self.export_selected()
            self.mode = 'list'
            self.current_page = 0
            self.cursor_pos = 0
        elif key == 27:  # Esc
            self.mode = 'list'
            self.current_page = 0
            self.cursor_pos = 0
        elif key in (ord('s'), ord('S')):
            self.mode = 'summary'
            self.current_page = 0
        elif key in (ord('l'), ord('L')):
            self.mode = 'list'
            self.current_page = 0
            self.cursor_pos = 0
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
    filename = "input.json"  # Specify your input file here
    app = JsonViewer(stdscr, filename)
    app.run()

if __name__ == "__main__":
    curses.wrapper(main)
