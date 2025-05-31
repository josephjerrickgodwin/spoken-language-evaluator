import logging
import os
import whisper

# !--- Configure logging ---
logger = logging.getLogger(__name__)


class AudioTranscribeService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AudioTranscribeService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, model_name: str = "base"):
        """
        Initializes the AudioTranscribeService instance

        Args:
            model_name (str): The name of the Whisper model to use.
                              Options include "tiny", "base", "small", "medium", "large".
                              Larger models offer better accuracy but require more resources
                              and download time. "base" is a good starting point.
        """
        self.model_name = model_name
        self.model = None

        # Load the Whisper model. This will download the model if it's not already cached.
        self._load_model()

    def _load_model(self):
        """
        Loads the Whisper model specified by the instance's model_name attribute.
        """
        logger.info(f"Loading Whisper model: '{self.model_name}'...")
        self.model = whisper.load_model(self.model_name)
        logger.info("Model loaded successfully.")

    def transcribe_audio_to_text(self, audio_file_path: str):
        """
        Transcribes an audio file (e.g., MP3) to text using the Whisper ASR model.

        Args:
            audio_file_path (str): The path to the audio file (e.g., 'audio.mp3').

        Returns:
            str: The transcribed text, or None if an error occurs.
        """
        if not os.path.exists(audio_file_path):
            logger.error(
                f"Error: Audio file not found at '{audio_file_path}'"
            )
            return None

        try:
            logger.info(
                "Starting audio transcription..."
            )

            # Transcribe the audio file.
            result = self.model.transcribe(audio_file_path)

            # Extract the transcribed text.
            transcribed_text = result["text"]
            logger.info(
                "Audio transcription completed successfully!"
            )
            return transcribed_text

        except Exception as e:
            logger.error(
                f"An error occurred during transcription: {str(e)}"
            )
            return None


audio_transcribe_service = AudioTranscribeService()
