import logging
import uuid

from src.exception.audio_extraction_exception import AudioExtractionException
from src.exception.audio_transcribe_exception import AudioTranscribeException
from src.exception.candidate_language_exception import CandidateLanguageException
from src.exception.video_conversion_exception import VideoConversionException
from src.service.audio.audio_conversion_service import audio_conversion_service
from src.service.audio.audio_transcribe_service import audio_transcribe_service
from src.service.language.english_accent_classifier_service import english_accent_classifier_service
from src.service.language.language_identification_service import language_identification_service
from src.service.utils.cache_service import cache_service
from src.service.utils.transcription_summarizer_service import transcription_summarization_service
from src.service.utils.video_downloader_service import video_downloader_service

# !--- Configure logging ---
logger = logging.getLogger(__name__)


class CandidateEvaluatorService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CandidateEvaluatorService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def _create_task_id(cls) -> str:
        """
        Generates a unique filename using a UUID and the configured video extension.

        Returns:
            str: The generated filename with extension.
        """
        return str(uuid.uuid4()).replace('-', '_')

    @classmethod
    def _create_cache(cls, session_id: str):
        return cache_service.create_cache(session_id=session_id)

    @classmethod
    def _remove_cache(cls, session_id: str):
        cache_removed = cache_service.delete_cache(session_id=session_id)
        if not cache_removed:
            logger.warning(
                f'Failed to remove cache: {session_id}. Please consider removing them manually.'
            )

    async def evaluate(self, video_url: str):
        """
        Evaluates a candidate's video by downloading it, extracting and transcribing audio,
        verifying English language, classifying accent, and generating a summary.

        Args:
            video_url (str): The URL of the candidate's video.

        Returns:
            tuple: (score, accent, summary) where score is the accent classification score,
            accent is the detected English accent, and summary is the LLM-generated analysis.

        Raises:
            VideoConversionException: If the video cannot be downloaded.
            AudioExtractionException: If audio extraction fails.
            AudioTranscribeException: If audio transcription fails.
            CandidateLanguageException: If the detected language is not English.
        """
        task_id = self._create_task_id()

        # Create the cache for the current task
        cache_path = cache_service.create_cache(session_id=task_id)

        # Step 1: Download the video from the url
        video_path = await video_downloader_service.download_video(
            cache_path=cache_path,
            url=video_url
        )
        if video_path is None:
            self._remove_cache(session_id=task_id)
            raise VideoConversionException(
                "Could not download the video. "
                "Please make sure that the video exists and appropriate permissions are given."
            )

        # Step 2: Extract the audio from the video
        audio_path = audio_conversion_service.extract_audio(
            cache_path=cache_path,
            video_path=video_path
        )
        if audio_path is None:
            self._remove_cache(session_id=task_id)
            raise AudioExtractionException(
                "Could not extract the audio. Please make sure the validity of the video."
            )

        # Step 3: Transcribe audio using Whisper
        audio_transcription = audio_transcribe_service.transcribe_audio_to_text(
            audio_file_path=audio_path
        )
        if audio_transcription is None:
            self._remove_cache(session_id=task_id)
            raise AudioTranscribeException(
                "Could not transcribe the audio. Please try again later."
            )

        # Step 4: Detect the speaker's language and verify its English
        candidate_language, probability = language_identification_service.predict_language(
            text=audio_transcription
        )
        if candidate_language != 'English':
            self._remove_cache(session_id=task_id)
            raise CandidateLanguageException(
                detected_language=candidate_language,
                probability=probability
            )

        # Step 5: Classify the English accent of the speaker
        score, accent = english_accent_classifier_service.classify(
            audio_file_path=audio_path
        )

        # Step 6: Analyze accent using the LLM based on the transcription
        summary = transcription_summarization_service.summarize(
            audio_transcription=audio_transcription
        )

        # Remove the cache upon successful completion
        self._remove_cache(session_id=task_id)

        return score, accent, summary


candidate_evaluator_service = CandidateEvaluatorService()
