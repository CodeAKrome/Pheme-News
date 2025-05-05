import ollama
from json import loads
import sys


class OllamaAI:
    def __init__(self, model="llama3.1:8b", system_prompt=None, temperature=0.1):
        self.model = model
        self.temperature = temperature
        self.set_system(system_prompt)

    def set_system(self, prompt):
        self.system = (
            prompt
            or "You are a helpful assistant. You reply with short, accurate answers. You will always reply using JSON. You will not include any markdown or other text outside of the JSON format."
        )

    def says(self, prompt):
        message = {"role": "user", "content": prompt}

        sys.stderr.write(f"\n===\nSYS:\n{self.system}\nPROM:\n{prompt}\n---\n")

        response = ollama.chat(
            model=self.model,
            messages=[message],
            stream=False,
            options={"temperature": self.temperature, "system": self.system},
            # options={"temperature": self.temperature, "system": self.system, "format": "json"},
        )
        return response["message"]["content"]
        # sys.stderr.write(f"RAW JSON: {response['message']['content']}\n")
        # ans = response['message']['content'][8:-4]
        # sys.stderr.write(f"TRIM JSON: {ans}\n")
        # return loads(ans)


if __name__ == "__main__":
    ai = OllamaAI()
    print(ai.says("What is the capital of France? You will reply using JSON."))
