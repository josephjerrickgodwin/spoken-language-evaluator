import logging

from summarizer import Summarizer

from src.exception.transcription_summarization_exception import TranscriptionSummarizationException


# !--- Configure logging ---
logger = logging.getLogger(__name__)


class TranscriptionSummarizationService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TranscriptionSummarizationService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, num_sentences: int = 3):
        self.model = Summarizer()
        self.num_sentences = num_sentences

    def summarize(self, audio_transcription: str):
        try:
            logger.info(
                "Started generating summary for the transcription. This may take a while..."
            )
            summary = self.model(audio_transcription, num_sentences=self.num_sentences)
            logger.info(
                "Successfully generated summary for the transcription."
            )
            return summary
        except Exception as e:
            raise TranscriptionSummarizationException(
                f"Failed to generate summary for the audio transcription. Details: {str(e)}"
            )


transcription_summarization_service = TranscriptionSummarizationService()
