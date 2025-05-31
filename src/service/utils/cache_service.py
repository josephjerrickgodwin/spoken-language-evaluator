import logging
import os
import shutil
from typing import List, Optional

# !--- Configure logging ---
logger = logging.getLogger(__name__)


class CacheService:
    """
    Service for managing local cache folders based on session IDs.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CacheService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, base_cache_dir_name: str = "cache"):
        """
        Initialize the CacheService.

        Args:
            base_cache_dir_name (str): The base directory name where session cache folders are stored.
        """
        self.base_cache_dir = os.path.join(os.getcwd(), base_cache_dir_name)
        os.makedirs(self.base_cache_dir, exist_ok=True)
        logger.debug(
            f"Initialized CacheService with base_cache_dir: {self.base_cache_dir}"
        )

    def _session_path(self, session_id: str) -> str:
        """Get the absolute path for a session's cache folder."""
        path = os.path.join(self.base_cache_dir, session_id)
        logger.debug(
            f"Computed session path for session_id '{session_id}': {path}"
        )
        return path

    def create_cache(self, session_id: str) -> str:
        """
        Create a cache folder for the given session ID.

        Args:
            session_id (str): The session identifier.

        Returns:
            str: The path to the created cache folder.
        """
        path = self._session_path(session_id)
        os.makedirs(path, exist_ok=True)
        logger.debug(
            f"Created cache directory for session_id '{session_id}': {path}"
        )
        return path

    def list_caches(self) -> List[str]:
        """
        List all session cache folders.

        Returns:
            List[str]: List of session IDs with cache folders.
        """
        caches = [
            name for name in os.listdir(self.base_cache_dir)
            if os.path.isdir(os.path.join(self.base_cache_dir, name))
        ]
        logger.debug(
            f"Listed caches in '{self.base_cache_dir}': {caches}"
        )
        return caches

    def cache_exists(self, session_id: str) -> bool:
        """
        Check if a cache folder exists for the given session ID.

        Args:
            session_id (str): The session identifier.

        Returns:
            bool: True if the cache folder exists, False otherwise.
        """
        exists = os.path.isdir(self._session_path(session_id))
        logger.debug(
            f"Cache exists for session_id '{session_id}': {exists}"
        )
        return exists

    def rename_cache(self, old_session_id: str, new_session_id: str) -> Optional[str]:
        """
        Rename a session's cache folder.

        Args:
            old_session_id (str): The current session ID.
            new_session_id (str): The new session ID.

        Returns:
            Optional[str]: The new path if successful, None if the old folder doesn't exist.
        """
        old_path = self._session_path(old_session_id)
        new_path = self._session_path(new_session_id)
        if not os.path.isdir(old_path):
            logger.debug(
                f"Cannot rename cache: old session_id '{old_session_id}' does not exist at '{old_path}'"
            )
            return None
        os.rename(old_path, new_path)
        logger.debug(
            f"Renamed cache from '{old_session_id}' ({old_path}) to '{new_session_id}' ({new_path})"
        )
        return new_path

    def delete_cache(self, session_id: str) -> bool:
        """
        Delete a session's cache folder.

        Args:
            session_id (str): The session identifier.

        Returns:
            bool: True if the folder was deleted, False if it didn't exist.
        """
        path = self._session_path(session_id)
        if os.path.isdir(path):
            shutil.rmtree(path)
            logger.debug(
                f"Deleted cache directory for session_id '{session_id}': {path}"
            )
            return True
        logger.debug(
            f"Cache directory for session_id '{session_id}' does not exist: {path}"
        )
        return False


cache_service = CacheService()
