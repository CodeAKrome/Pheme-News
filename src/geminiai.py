import os
import sys
from google.generativeai import GenerativeModel, configure
import requests
from PIL import Image
from io import BytesIO
import fire
import base64

DEFAULT_MODEL = "gemini-1.5-pro"
DEFAULT_MODEL = "gemini-1.5-flash"
DEFAULT_MODEL = "gemini-2.0-flash-thinking-exp-1219"


class GeminiAI:
    def __init__(
        self,
        system_prompt=None,
        model=DEFAULT_MODEL,
        max_tokens=6000,
        temperature=0.1,
        api_key=None,
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        configure(api_key=self.api_key)

        self.model = GenerativeModel(model)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.set_system(system_prompt)

    def set_system(self, prompt):
        self.prompt = (
            prompt
            or "You are a helpful assistant. You reply with short, accurate answers."
        )
        self.chat = self.model.start_chat(history=[])
        self.chat.send_message(self.prompt)

    def load_image(self, PathUrlBase64):
        """
        Returns an image object from a path, URL or base64 encoded image data.
        """
        if PathUrlBase64.startswith(("http://", "https://")):
            response = requests.get(PathUrlBase64)
            img = Image.open(BytesIO(response.content))
        elif PathUrlBase64.startswith("data:image"):
            # Handle base64 encoded image data
            img_data = PathUrlBase64.split(",")[1]
            img = Image.open(BytesIO(base64.b64decode(img_data)))
        else:
            img = Image.open(PathUrlBase64)
        return img

    def says(self, prompt, image_path_or_url=None):
        content = [prompt]

        if image_path_or_url:
            image = self.load_image(image_path_or_url)
            content.append(image)

        try:
            response = self.model.generate_content(
                content,
                generation_config={
                    "max_output_tokens": self.max_tokens,
                    "temperature": self.temperature,
                },
            )
        except Exception as e:
            sys.stderr.write(f"Error generating content: {e}\n")
            return None

        return response.text


def load_from_file(file_path):
    with open(file_path, "r") as file:
        return file.read().strip()


def main(
    prompt=None,
    prompt_file=None,
    image=None,
    system_prompt=None,
    system_prompt_file=None,
):
    """
    Interact with GeminiAI.

    Args:
        prompt (str, optional): The main prompt for the AI.
        prompt_file (str, optional): Path to a file containing the main prompt.
        image (str, optional): Path or URL to an image.
        system_prompt (str, optional): System prompt for the AI.
        system_prompt_file (str, optional): Path to a file containing the system prompt.
    """
    if prompt_file:
        prompt = load_from_file(prompt_file)
    elif not prompt:
        raise ValueError("Either 'prompt' or 'prompt_file' must be provided.")

    if system_prompt_file:
        system_prompt = load_from_file(system_prompt_file)

    gemini = GeminiAI(system_prompt=system_prompt)
    response = gemini.says(prompt, image)
    print(response)


if __name__ == "__main__":
    fire.Fire(main)
