import os
import re
import asyncio
import uuid
from typing import LiteralString, Union

import aiohttp
import yt_dlp
import logging

# !--- Configure logging ---
logger = logging.getLogger(__name__)

# !--- Patterns for platform detection
video_extensions = ('.mp4', '.mov', '.avi', '.webm', '.mkv', '.flv', '.ogg', '.ogv')
youtube_pattern = r'^https?://(?:www\.)?(youtube\.com/watch\?v=|youtu\.be/)'
vimeo_pattern = r'^https?://(?:www\.)?vimeo\.com/'


class VideoDownloaderService:
    """
    Provides a singleton service for downloading videos from various sources, including direct video links,
    Loom, YouTube, and Vimeo. Supports asynchronous downloads using aiohttp for direct links and yt-dlp
    for platform-based videos with intelligent URL detection.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures that only one instance of VideoDownloaderService is created (singleton pattern).
        Returns the existing instance if it exists; otherwise, creates and returns a new one.
        """
        if not cls._instance:
            cls._instance = super(VideoDownloaderService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, video_extension: str = 'mp4'):
        """
        Initializes the VideoDownloaderService instance by setting the download directory.
        
        Creates the specified download directory if it does not exist and logs the directory path.
        
        Args:
            video_extension (str, optional): The extension of the video to download. Defaults to '.mp4'
        """
        self.video_extension = video_extension

        # ydl configurations
        self.retries = 5
        self.noplaylist = True
        self.quiet = True
        self.no_warnings = True

    def _create_file_name(self) -> str:
        """
        Generates a unique filename using a UUID and the configured video extension.

        Returns:
            str: The generated filename with extension.
        """
        file_name = str(uuid.uuid4()).replace('-', '_')
        return f'{file_name}.{self.video_extension}'

    @classmethod
    async def _download_general_video(cls, cache_path: str, url: str) -> Union[LiteralString, str, bytes, None]:
        """
        Asynchronously downloads a video from a direct URL using aiohttp.

        Attempts to infer the filename from the Content-Disposition header if not provided.
        Saves the video to the configured download directory.

        Args:
            cache_path (str): Path to store the downloaded video file
            url (str): The URL of the video to download.

        Returns:
            Union[LiteralString | str | bytes | None]: The path to the downloaded file if successful, otherwise None.
        """
        try:
            async with aiohttp.ClientSession() as session, session.get(url) as response:
                response.raise_for_status()

                logger.info(
                    f"Starting async download from {url} to {cache_path}"
                )
                with open(cache_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(8192):
                        chunk = await chunk
                        f.write(chunk)

            logger.info(
                f"Video downloaded successfully to: {cache_path}"
            )
            return cache_path

        except aiohttp.ClientError as e:
            logger.error(
                f"aiohttp client error downloading {url}: {e}"
            )
        except asyncio.TimeoutError:
            logger.error(
                f"Download of {url} timed out."
            )
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during general video download of {url}: {e}"
            )
        return None

    async def _download_loom_video(self, cache_path: str, url: str) -> Union[str, None]:
        """
        Asynchronously downloads a Loom video using yt-dlp.

        Args:
            cache_path (str): Path to store the downloaded video file
            url (str): The URL of the video to download.

        Returns:
            Union[str, None]: The path to the downloaded file if successful, otherwise None.
        """
        logger.info(f"Attempting to download Loom video with yt-dlp from {url}")

        # Initialize the yt_dlp parameters
        ydl_options = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': cache_path,
            'merge_output_format': f'.{self.video_extension}',
            'retries': self.retries,
            'noplaylist': self.noplaylist,
            'quiet': self.quiet,
            'no_warnings': self.no_warnings,
            'logger': logger,
        }

        try:
            loop = asyncio.get_running_loop()
            info = await loop.run_in_executor(
                None,
                lambda: self._run_yt_dlp_extract(
                    url=url,
                    ydl_options=ydl_options
                )
            )
            if not info:
                logger.error(
                    f"yt-dlp failed to extract info or download for {url}"
                )
                return None

            # Return the file path of the downloaded video, if the download is successful.
            downloaded_file = info.get('filepath') or info.get('_format_filepath')
            if downloaded_file and os.path.exists(downloaded_file):
                logger.info(
                    f"Loom video downloaded successfully to: {downloaded_file}"
                )
                return downloaded_file

            logger.error(
                f"yt-dlp completed, but could not determine downloaded file path for {url}"
            )
        except yt_dlp.utils.DownloadError as e:
            logger.error(
                "An unexpected error occurred while downloading Loom video. "
                "Please check for correct permissions."
            )
        except Exception as e:
            logger.error(
                f"An unexpected error occurred during Loom video download for {url}: {e}"
            )
        return None

    @classmethod
    def _run_yt_dlp_extract(cls, url: str, ydl_options: dict) -> dict:
        """
        Synchronously extracts video information and downloads the video from the given URL using yt-dlp.
        
        Args:
            url (str): The URL of the video to download.
            ydl_options (dict): yt-dlp options for extraction and download.
        
        Returns:
            dict: Information about the downloaded video as returned by yt-dlp.
        """
        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            return ydl.extract_info(url, download=True)

    async def download_video(self, cache_path: str, url: str) -> Union[LiteralString, str, bytes, None]:
        """
        Asynchronously downloads a video from the given URL, automatically detecting the platform
        (direct link, Loom, YouTube, or Vimeo) and selecting the appropriate download method.

        Args:
            cache_path (str): Path to store the downloaded video file
            url (str): The URL of the video to download.

        Returns:
            Union[LiteralString | str | bytes | None]: The path to the downloaded file if successful, otherwise None.
        """
        # Add video extension to the file name
        file_name = self._create_file_name()

        # Absolute path to the video file
        cache_path = os.path.join(cache_path, file_name)

        # Start downloading the video
        logger.info(f"Attempting to download video from URL: {url}")
        if "loom.com/share/" in url:
            logger.info(
                f"URL identified as a Loom link: {url}"
            )
            return await self._download_loom_video(
                cache_path=cache_path,
                url=url
            )
        if url.lower().endswith(video_extensions):
            logger.info(
                f"URL identified as a direct video file link (based on extension): {url}"
            )
            return await self._download_general_video(
                cache_path=cache_path,
                url=url
            )
        if re.match(youtube_pattern, url):
            logger.info(
                f"URL identified as a YouTube link: {url}. Using yt-dlp."
            )
            return await self._download_loom_video(
                cache_path=cache_path,
                url=url
            )
        if re.match(vimeo_pattern, url):
            logger.info(
                f"URL identified as a Vimeo link: {url}. Using yt-dlp."
            )
            return await self._download_loom_video(
                cache_path=cache_path,
                url=url
            )

        logger.warning(
            f"URL type not explicitly identified. Attempting general download: {url}"
        )
        return await self._download_general_video(
            cache_path=cache_path,
            url=url
        )


video_downloader_service = VideoDownloaderService()
