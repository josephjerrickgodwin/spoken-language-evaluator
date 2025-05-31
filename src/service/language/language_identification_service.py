import logging
from typing import Tuple, Any

from langdetect import DetectorFactory, detect_langs

# !--- Reset seed to avoid ambiguity
DetectorFactory.seed = 0

# !--- Configure logging ---
logger = logging.getLogger(__name__)


class LanguageIdentificationService:
    """
    Singleton service for detecting the language of a given text using language detection libraries.

    Provides a method to predict the language and its probability, returning the language name in English.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LanguageIdentificationService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initializes the LanguageIdentificationService instance and sets up a mapping from language
        codes to their English names.
        """
        self.language_map = {
            "af": "Afrikaans", "ar": "Arabic", "bg": "Bulgarian", "bn": "Bengali", "ca": "Catalan",
            "cs": "Czech", "cy": "Welsh", "da": "Danish", "de": "German", "el": "Greek", "en": "English",
            "es": "Spanish", "et": "Estonian", "fa": "Persian", "fi": "Finnish", "fr": "French",
            "gu": "Gujarati", "he": "Hebrew", "hi": "Hindi", "hr": "Croatian", "hu": "Hungarian",
            "id": "Indonesian", "it": "Italian", "ja": "Japanese", "kn": "Kannada", "ko": "Korean",
            "lt": "Lithuanian", "lv": "Latvian", "mk": "Macedonian", "ml": "Malayalam", "mr": "Marathi",
            "ne": "Nepali", "nl": "Dutch", "no": "Norwegian", "pa": "Punjabi", "pl": "Polish",
            "pt": "Portuguese", "ro": "Romanian", "ru": "Russian", "sk": "Slovak", "sl": "Slovenian",
            "so": "Somali", "sq": "Albanian", "sv": "Swedish", "sw": "Swahili", "ta": "Tamil",
            "te": "Telugu", "th": "Thai", "tl": "Tagalog", "tr": "Turkish", "uk": "Ukrainian", "ur": "Urdu",
            "vi": "Vietnamese", "zh-cn": "Chinese (Simplified)", "zh-tw": "Chinese (Traditional)"
        }

    def predict_language(self, text: str) -> tuple[str | Any, float | Any]:
        """
        Detects the language of the given text and returns the language name along with its probability.

        Args:
            text (str): The input text to analyze.

        Returns:
            Tuple[str, float]: The detected language in English and its probability score.
        """
        logger.info(
            "Started identifying language of the audio transcription."
        )
        detected_languages = detect_langs(text)

        # Extract the detection details
        language = ''
        probability = 0.0
        if detected_languages:
            detected_language = detected_languages[0]
            language = detected_language.lang
            probability = detected_language.prob

        # Convert the language to a fully-qualified English term
        language = self.language_map.get(language, 'Undefined')

        logger.info(
            f"Successfully identified the audio transcription language. "
            f"Language is: {language} with a probability of {probability}"
        )
        return language, probability


language_identification_service = LanguageIdentificationService()
