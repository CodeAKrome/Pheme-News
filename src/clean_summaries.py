import re


def clean_summaries(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove all lines starting with "**Summary:**" and any subsequent lines until a blank line is found.
    cleaned_content = re.sub(
        r"\n\*\*Summary:\*\*.*?(\n\n|\Z)", "\n", content, flags=re.DOTALL
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(cleaned_content.strip() + "\n")


if __name__ == "__main__":
    clean_summaries("/Users/kyle/hub/Pheme-News/tmp/top10.md")
