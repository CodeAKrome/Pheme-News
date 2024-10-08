import os
import sys
from google.generativeai import GenerativeModel, configure
import requests
from PIL import Image
from io import BytesIO

#DEFAULT_MODEL = "gemini-1.5-pro-vision"
#DEFAULT_MODEL = "gemini-1.5-flash"
DEFAULT_MODEL = "gemini-1.5-pro"

class GeminiAI:
    def __init__(self, system_prompt=None, model=DEFAULT_MODEL, max_tokens=1500, temperature=0.1, api_key=None):
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

    def load_image(self, image_path_or_url):
        if image_path_or_url.startswith(('http://', 'https://')):
            response = requests.get(image_path_or_url)
            img = Image.open(BytesIO(response.content))
        else:
            img = Image.open(image_path_or_url)
        return img

    def says(self, prompt, image_path_or_url=None):
        content = [prompt]

        if image_path_or_url:
            image = self.load_image(image_path_or_url)
            content.append(image)

        response = self.model.generate_content(
            content,
            generation_config={
                "max_output_tokens": self.max_tokens,
                "temperature": self.temperature
            }
        )

        return response.text

if __name__ == "__main__":
    gemini = GeminiAI()

    if len(sys.argv) > 2:
        response = gemini.says(sys.argv[1], sys.argv[2])
    else:
        response = gemini.says(sys.argv[1])

    print(response)
