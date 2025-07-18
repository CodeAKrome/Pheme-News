#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple text translation utility using MyMemory Translation API or Google Translate.
This script provides functions to translate text between different languages using 2-letter language codes.
It can be used for quick translations without requiring an API key for MyMemory.
For Google Translate, it requires the `googletrans` library.
"""

import requests
from typing import Optional


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text from source language to target language using 2-letter language codes.

    Args:
        text (str): The text to translate
        source_lang (str): 2-letter source language code (e.g., 'en', 'es', 'fr')
        target_lang (str): 2-letter target language code (e.g., 'en', 'es', 'fr')

    Returns:
        str: Translated text

    Raises:
        Exception: If translation fails or API request fails
    """

    # MyMemory Translation API (free, no API key required)
    url = "https://api.mymemory.translated.net/get"

    params = {"q": text, "langpair": f"{source_lang}|{target_lang}"}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data["responseStatus"] == 200:
            return data["responseData"]["translatedText"]
        else:
            raise Exception(
                f"Translation failed: {data.get('responseDetails', 'Unknown error')}"
            )

    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except KeyError as e:
        raise Exception(f"Unexpected API response format: {str(e)}")


# Alternative implementation using Google Translate (requires googletrans library)
def translate_text_google(text: str, source_lang: str, target_lang: str) -> str:
    """
    Alternative translation function using Google Translate.
    Requires: pip install googletrans==4.0.0-rc1

    Args:
        text (str): The text to translate
        source_lang (str): 2-letter source language code
        target_lang (str): 2-letter target language code

    Returns:
        str: Translated text
    """
    try:
        from googletrans import Translator

        translator = Translator()
        result = translator.translate(text, src=source_lang, dest=target_lang)
        return result.text

    except ImportError:
        raise Exception(
            "googletrans library not installed. Run: pip install googletrans==4.0.0-rc1"
        )
    except Exception as e:
        raise Exception(f"Translation failed: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Example translations
    try:
        # English to Spanish
        result1 = translate_text("Hello, how are you?", "en", "es")
        print(f"EN -> ES: {result1}")

        # Spanish to French
        result2 = translate_text("Hola, ¿cómo estás?", "es", "fr")
        print(f"ES -> FR: {result2}")

        # French to English
        result3 = translate_text("Bonjour, comment allez-vous?", "fr", "en")
        print(f"FR -> EN: {result3}")

    except Exception as e:
        print(f"Error: {e}")


# Common language codes reference
LANGUAGE_CODES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "hi": "Hindi",
    "nl": "Dutch",
    "sv": "Swedish",
    "da": "Danish",
    "no": "Norwegian",
    "fi": "Finnish",
    "pl": "Polish",
    "tr": "Turkish",
    "th": "Thai",
}
