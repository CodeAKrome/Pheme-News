from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
import torch


class Xl8:
    def __init__(self, max_tokens=1200):
        self.max_tokens = max_tokens
        self.model_name = "facebook/mbart-large-50-many-to-many-mmt"
        self.device = self._grafix_device()
        self.model = MBartForConditionalGeneration.from_pretrained(self.model_name).to(
            self.device
        )
        self.tokenizer = MBart50TokenizerFast.from_pretrained(self.model_name)
        self.lang_code_map = self._create_lang_code_map()
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def _grafix_device(self):
        """Return device to use for GPU"""
        device = "cpu"
        if torch.backends.mps.is_available():
            device = "mps"
        if torch.cuda.is_available():
            device = "cuda"
        return device

    def _create_lang_code_map(self):
        return {
            lang_code.split("_")[0]: lang_code
            for lang_code in self.tokenizer.lang_code_to_id.keys()
        }

    def translate(self, text, source_lang, target_lang, max_tokens):
        """
        Translate the given text from source language to target language.

        :param text: The text to translate
        :param source_lang: The source language code (e.g., 'en', 'fr', 'hi')
        :param target_lang: The target language code (e.g., 'en', 'fr', 'hi')
        :param max_length: Maximum length of the generated translation
        :return: tuple(Translated text, input token count, output token count)
        """
        try:
            src_lang_code = self.lang_code_map.get(source_lang)
            tgt_lang_code = self.lang_code_map.get(target_lang)

            if not src_lang_code or not tgt_lang_code:
                raise ValueError(
                    f"Unsupported language code: {source_lang} or {target_lang}"
                )

            self.tokenizer.src_lang = src_lang_code
            encoded = self.tokenizer(text, return_tensors="pt").to(self.device)

            input_tokens = encoded["input_ids"].shape[1]
            self.total_input_tokens += input_tokens

            max_new_tokens = max(max_tokens - input_tokens, 1)

            generated_tokens = self.model.generate(
                **encoded,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_lang_code],
                max_new_tokens=max_new_tokens,
            )

            output_tokens = generated_tokens.shape[1]
            self.total_output_tokens += output_tokens

            translated_text = self.tokenizer.batch_decode(
                generated_tokens, skip_special_tokens=True
            )[0]
            return translated_text, input_tokens, output_tokens
        except Exception as e:
            return f"Translation error: {str(e)}", 0, 0

    def get_supported_languages(self):
        """
        Get a list of supported languages.

        :return: List of supported language codes
        """
        return list(self.lang_code_map.keys())

    def translate_article(
        self, article, source_lang, target_lang="en", max_tokens=None
    ):
        """
        Translate a news article to the target language (default is English).

        :param article: The news article text
        :param source_lang: The source language code
        :param target_lang: The target language code (default: 'en' for English)
        :param max_length: Maximum length of the generated translation
        :return: tuple(Translated article, input token count, output token count)
        """
        if max_tokens is None:
            max_tokens = self.max_tokens

        return self.translate(article, source_lang, target_lang, max_tokens)

    def get_token_usage(self):
        """
        Get the total number of input and output tokens processed.

        :return: tuple(Total input tokens, Total output tokens)
        """
        return self.total_input_tokens, self.total_output_tokens


# Example usage
if __name__ == "__main__":
    translator = Xl8()

    # Example articles in different languages
    articles = {
        "hi": "संयुक्त राष्ट्र के प्रमुख का कहना है कि सीरिया में कोई सैन्य समाधान नहीं है",
        "ar": "الأمين العام للأمم المتحدة يقول إنه لا يوجد حل عسكري في سوريا.",
        "fr": "Le président français a annoncé de nouvelles mesures économiques aujourd'hui.",
        "de": "Die deutsche Wirtschaft zeigt Anzeichen der Erholung nach der globalen Krise.",
    }

    for lang, article in articles.items():
        print(f"Original ({lang}):", article)
        translated, input_tokens, output_tokens = translator.translate_article(
            article, lang, max_tokens=1200
        )
        print(f"Translated to English: {translated}")
        print(f"Input tokens: {input_tokens}, Output tokens: {output_tokens}")
        print()

    # Translate from English to French
    english_article = "The global economy shows signs of recovery after the pandemic."
    french_translation, input_tokens, output_tokens = translator.translate(
        english_article, "en", "fr", max_tokens=300
    )
    print(f"English to French translation: {french_translation}")
    print(f"Input tokens: {input_tokens}, Output tokens: {output_tokens}")
    print()

    # Print supported languages
    print("Supported languages:", ", ".join(translator.get_supported_languages()))

    # Print total token usage
    total_input, total_output = translator.get_token_usage()
    print(f"Total token usage - Input: {total_input}, Output: {total_output}")
