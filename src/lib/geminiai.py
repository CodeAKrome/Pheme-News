import os
import sys
from google.generativeai import GenerativeModel, configure

import os
from google.generativeai import GenerativeModel, configure

class GeminiAI:
    def __init__(self, system_prompt=None, model="gemini-1.5-pro", max_tokens=1500, temperature=0.1, api_key=None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        configure(api_key=self.api_key)

        self.model = GenerativeModel(model)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.set_system(system_prompt)

    def set_system(self, prompt):
        self.prompt = prompt or "You are a helpful assistant. You reply with short, accurate answers."
        self.chat = self.model.start_chat(history=[])
        self.chat.send_message(self.prompt)

    def says(self, prompt):
        response = self.chat.send_message(
            prompt,
            generation_config={
                "max_output_tokens": self.max_tokens,
                "temperature": self.temperature
            }
        )

        return response.text

if __name__ == "__main__":
    gemini = GeminiAI()
    response = gemini.says(sys.argv[1])
    print(response)
