class CandidateLanguageException(Exception):
    """
    Exception raised when the candidate language is not recognized or identified as a non-english speaker.

    Parameters:
        detected_language (str): The language detected for the candidate.
        probability (float): The probability/confidence of the detected language.
    """
    def __init__(self, detected_language: str, probability: float) -> None:
        message = (
            f"Candidate language '{detected_language}' detected with probability {probability:.2f} "
            "is not recognized or is a non-English speaker."
        )
        super().__init__(message)
        self._detected_language: str = detected_language
        self._probability: float = probability

    @property
    def detected_language(self) -> str:
        return self._detected_language

    @property
    def probability(self) -> float:
        return self._probability
