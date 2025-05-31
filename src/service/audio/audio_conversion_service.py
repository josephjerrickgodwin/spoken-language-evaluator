import os
import subprocess
import logging
import uuid

from src.service.utils.cache_service import CacheService

# !--- Configure logging ---
logger = logging.getLogger(__name__)


class AudioConversionService(CacheService):
    """
    Service for extracting audio from video files using FFmpeg, managing audio file naming,
    and handling cache directories for audio conversion sessions. Inherits cache management
    functionality and supports multiple audio formats.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AudioConversionService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, audio_extension: str = "mp3"):
        super(AudioConversionService, self).__init__()
        self.audio_extension = audio_extension

        # Define the FFmpeg codecs
        self.codec_map = {
            "mp3": "libmp3lame",
            "aac": "aac",
            "wav": "pcm_s16le",
            "flac": "flac",
            "ogg": "libvorbis"
        }

    def _create_file_name(self) -> str:
        """
        Generates a unique filename using a UUID and the configured video extension.

        Returns:
            str: The generated filename with extension.
        """
        file_name = str(uuid.uuid4()).replace('-', '_')
        return f'{file_name}.{self.audio_extension}'

    def extract_audio(self, cache_path: str, video_path: str) -> str | None:
        """
        Extracts audio from a video file using ffmpeg.

        Args:
            cache_path (str): Path to store the extracted audio file.
            video_path (str): Path to the downloaded video file.

        Returns:
            str | None: The path to the extracted audio file if successful, otherwise None.
        """
        if not os.path.exists(video_path):
            logger.error(
                f"Video file not found at: {video_path}"
            )
            return None

        # Add video extension to the file name
        file_name = self._create_file_name()

        # Absolute path to the audio file
        output_audio_path = os.path.join(cache_path, file_name)

        logger.info(
            f"Attempting to extract audio from '{video_path}' to '{output_audio_path}'"
        )

        # Select audio codec based on output format
        audio_codec = self.codec_map.get(self.audio_extension.lower(), "copy")

        # Initialize the ffmpeg command
        command = [
            "ffmpeg", "-i", video_path, "-vn", "-acodec", audio_codec,
            "-q:a", "0", "-y", output_audio_path
        ]

        try:
            # Run the ffmpeg command as a subprocess
            _ = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(
                f"Audio extraction successful: {output_audio_path}"
            )
            return output_audio_path

        except FileNotFoundError:
            logger.error(
                "FFmpeg not found. Please ensure ffmpeg is installed and in your system's PATH."
            )
        except subprocess.CalledProcessError as e:
            logger.error(
                f"FFmpeg command failed with error code {e.returncode} for '{video_path}'."
                f"FFmpeg stdout:\n{e.stdout}"
                f"FFmpeg stderr:\n{e.stderr}"
            )
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during audio extraction: {e}"
            )
        return None


audio_conversion_service = AudioConversionService()
