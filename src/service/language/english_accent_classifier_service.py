import logging
import os

import torch
from dotenv import load_dotenv
from speechbrain.inference import EncoderClassifier

from src.exception.english_accent_classification_exception import EnglishAccentClassificationException

load_dotenv()

# !--- Import the accent identification model name (hf)
ACCENT_IDENTIFICATION_MODEL = str(
    os.environ.get("ACCENT_IDENTIFICATION_MODEL", "Jzuluaga/accent-id-commonaccent_ecapa")
)

# !--- Configure logging ---
logger = logging.getLogger(__name__)


class EnglishAccentClassifierService:
    """
    Singleton service for classifying English accents in audio files using a pretrained model.
    Handles model loading, device selection (CPU or CUDA), and provides a method to classify audio files
    and return the predicted accent and confidence score.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EnglishAccentClassifierService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, model_cache_directory: str = 'model_cache/accent-id-commonaccent_ecapa'):
        """
        Initializes the EnglishAccentClassifierService by setting up the model cache directory,
        determining the device (CPU or CUDA), and loading the accent identification model for inference.

        Args:
            model_cache_directory (str, optional): Directory to cache the model files.
        """
        self.model_cache_directory = model_cache_directory

        # Determine the device (GPU support)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Initially the model should be empty
        self.model = None

        # Make a directory to store model cache
        os.makedirs(model_cache_directory, exist_ok=True)

        # Load the accent identification model
        self._load_model()

    def _load_model(self):
        """
        Loads the accent classifier model using the specified model source and device.
        Initializes the model for inference and logs the loading process.
        """
        logger.debug("Loading the accent classifier model...")
        if self.device == 'cuda':
            self.model = EncoderClassifier.from_hparams(
                source=ACCENT_IDENTIFICATION_MODEL,
                run_opts={"device": 'cuda'},
                savedir=self.model_cache_directory
            )
        else:
            self.model = EncoderClassifier.from_hparams(
                source=ACCENT_IDENTIFICATION_MODEL,
                savedir=self.model_cache_directory
            )
        logger.debug("Successfully loaded the accent classifier model...")

    def classify(self, audio_file_path: str):
        """
        Classifies the accent in the given audio file.

        Args:
            audio_file_path (str): Path to the audio file to be classified.

        Returns:
            tuple: A tuple containing the confidence, score, and predicted accent label.
        """
        logger.info(
            f"Started classifying audio: {audio_file_path}"
        )
        try:
            _, score, _, accent = self.model.classify_file(audio_file_path)

            # Convert the tensor to string
            score = f'{round(score.item(), 2) * 100}%'

            # Extract the accent
            accent: str = accent[0].capitalize()

            logger.info(
                f"Classification for audio: {audio_file_path} - Accent: {accent} with score: {score}"
            )
            return score, accent

        except Exception as e:
            raise EnglishAccentClassificationException(
                f"English language accent classification error due to: {str(e)}"
            )


english_accent_classifier_service = EnglishAccentClassifierService()
