from enum import Enum


class Colorize:
    def __init__(self):
        self.CHECK = "\u2713"
        self.CROSS = "\u2717"
        self.HEADER = "\033[95m"
        self.BLUE = "\033[94m"
        self.GREEN = "\033[92m"
        self.YELLOW = "\033[93m"
        self.RED = "\033[91m"
        self.ENDC = "\033[0m"
        self.BOLD = "\033[1m"
        self.UNDERLINE = "\033[4m"
        self.BOLD_OFF = "\033[21m"
        self.ITALIC = "\033[3m"
        self.BLINK = "\033[5m"
        self.BLINK_OFF = "\033[25m"
        self.SELECTED = "\033[7m"
        self.INVISIBLE = "\033[8m"
        self.STRIKETHROUGH = "\033[9m"
        self.RESET = "\033[0m"
        self.SELECTED_OFF = "\033[27m"
        self.INVISIBLE_OFF = "\033[28m"
        self.STRIKETHROUGH_OFF = "\033[29m"

    def colorize(self, text, color_code):
        return f"{color_code}{text}{self.ENDC}"

    def title(self, text):
        return self.colorize(text, self.BLUE)

    def info(self, text):
        return self.colorize(text, self.GREEN)

    def error(self, text):
        return self.colorize(text, self.RED)

    def warning(self, text):
        return self.colorize(text, self.YELLOW)

    def bold(self, text):
        return self.colorize(text, self.BOLD)

    def underline(self, text):
        return self.colorize(text, self.UNDERLINE)

    def italic(self, text):
        return self.colorize(text, self.ITALIC)

    def blink(self, text):
        return self.colorize(text, self.BLINK)

    def selected(self, text):
        return self.colorize(text, self.SELECTED)

    def invisible(self, text):
        return self.colorize(text, self.INVISIBLE)

    def strikethrough(self, text):
        return self.colorize(text, self.STRIKETHROUGH)

    def reset_all(self, text):
        return f"{self.RESET}{text}"

    def reset(self, text):
        return f"{self.RESET}{text}"


if __name__ == "__main__":
    # Example usage
    color = Colorize()
    print(color.title("This is a title."))
    print(color.info("This is an info message."))
    print(color.error("This is an error message."))
    print(color.warning("This is a warning message."))
    print(color.bold("This text is bold."))
    print(color.underline("This text is underlined."))
    print(color.italic("This text is italic."))
    print(color.blink("This text blinks."))
    print(color.selected("This text is selected."))
    print(color.invisible("This text is invisible."))
    print(color.strikethrough("This text has a strikethrough."))
