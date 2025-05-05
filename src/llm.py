import ollama
import sys

# from dotenv import load_dotenv
from json import dumps
from json import loads, dumps, JSONDecodeError
from tqdm import tqdm

"""Read from stdin, take filename of system prompt and model on argv"""

# load_dotenv()


def main():
    if len(sys.argv) < 2:
        print("Usage: python llm.py system_prompt_filename models")
        sys.exit(1)

    system_file = sys.argv[1]
    model = sys.argv[2]
    with open(system_file, "r") as fh:
        system = fh.read()
    system = system.replace("\n", " ")
    # print(f"sys: {system}")
    model_file = f"\nFROM {model}\nSYSTEM {system}\n"
    # print(f"Model file: {model_file}")
    ollama.create(model=model, modelfile=model_file)

    for line in tqdm(sys.stdin):
        line = line.strip()
        if not line:
            continue
        try:
            data = loads(line)
        except JSONDecodeError as e:
            sys.stderr.write(f"JSON: {e}\n{line}\n")
            continue
        # This should mean this is an rss flavored record
        if not "ner" in data:
            print(line)
            continue
        # print(f"data: {data['text']}")
        response = ollama.generate(model=model, prompt=data["text"])
        data["llm"] = response["response"]
        print(dumps(data))


if __name__ == "__main__":
    main()
