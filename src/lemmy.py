#!/usr/bin/env python
import fire
import sys
import json
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# echo '{"content": "The quick brown foxes are running!"}' | ./lemmy.py process --field content


class TextProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()

    def clean_text(self, text):
        """Clean, tokenize, remove stop words, and lemmatize the input text."""
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation
        text = text.translate(str.maketrans("", "", string.punctuation))
        # Tokenize
        tokens = word_tokenize(text)
        # Remove stop words
        tokens = [token for token in tokens if token not in self.stop_words]
        # Lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        # Join tokens back into a string
        return " ".join(tokens)

    def process(self, jsonl=False, text=False, file=None, field="text"):
        """
        Process text input based on command-line options.

        Args:
            jsonl (bool): Read JSONL input from stdin (default mode).
            text (bool): Read plain text from stdin.
            file (str): Path to input text file.
            field (str): JSON field to extract text from (default: "text").
        """
        if sum([jsonl, text, file is not None]) > 1:
            raise ValueError(
                "Only one input mode (--jsonl, --text, --file) can be specified."
            )

        # Default to JSONL mode if no mode is specified
        if not jsonl and not text and not file:
            jsonl = True

        if file:
            # Read from file
            try:
                with open(file, "r", encoding="utf-8") as f:
                    input_text = f.read()
                processed_text = self.clean_text(input_text)
                print(processed_text)
            except FileNotFoundError:
                print(f"Error: File '{file}' not found.")
                sys.exit(1)
            except Exception as e:
                print(f"Error reading file: {e}")
                sys.exit(1)

        elif text:
            # Read plain text from stdin
            input_text = sys.stdin.read().strip()
            processed_text = self.clean_text(input_text)
            print(processed_text)

        elif jsonl:
            # Read JSONL from stdin
            for line in sys.stdin:
                try:
                    data = json.loads(line.strip())
                    if field not in data:
                        print(
                            f"Error: Field '{field}' not found in JSON: {line.strip()}"
                        )
                        continue
                    input_text = data[field]
                    processed_text = self.clean_text(input_text)
                    print(json.dumps({field: processed_text}))
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSONL: {line.strip()}")
                    continue
                except Exception as e:
                    print(f"Error processing JSONL: {e}")
                    continue


if __name__ == "__main__":
    fire.Fire(TextProcessor)
