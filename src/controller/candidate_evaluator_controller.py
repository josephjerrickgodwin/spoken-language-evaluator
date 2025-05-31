import logging

from fastapi import APIRouter, HTTPException, status

from src.exception.audio_extraction_exception import AudioExtractionException
from src.exception.audio_transcribe_exception import AudioTranscribeException
from src.exception.candidate_language_exception import CandidateLanguageException
from src.exception.english_accent_classification_exception import EnglishAccentClassificationException
from src.exception.transcription_summarization_exception import TranscriptionSummarizationException
from src.exception.video_conversion_exception import VideoConversionException
from src.model.candidate_evaluator_model import CandidateEvaluateResponse, CandidateEvaluateRequest
from src.service.candidate_evaluator_service import candidate_evaluator_service

router = APIRouter(
    prefix="/evaluation",
    tags=["Candidate Accent Evaluation Controller"]
)


@router.post(
    "/evaluate",
    summary="An endpoint for evaluating a candidate's English accent.",
    description="Identify and evaluate English accent with a confidence score.",
    response_model=CandidateEvaluateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        202: {
            "description": "Non-English speaker detected.",
            "content": {
                "application/json": {
                    "example": {
                        "detected_language": "Spanish",
                        "probability": 0.98,
                        "message": "Non-English speaker detected."
                    }
                }
            }
        },
        400: {
            "description": "Bad Request - Video conversion failed.",
            "content": {
                "application/json": {
                    "example": {"detail": "Video format not supported."}
                }
            }
        },
        422: {
            "description": "Unprocessable Entity - Invalid input.",
            "content": {
                "application/json": {
                    "example": {"detail": "Video URL is required."}
                }
            }
        },
        503: {
            "description": "Service Unavailable - Downstream processing failed.",
            "content": {
                "application/json": {
                    "example": {"detail": "Audio extraction failed."}
                }
            }
        },
        500: {
            "description": "Internal Server Error.",
            "content": {
                "application/json": {
                    "example": {"detail": "An internal server error occurred. Please try again later."}
                }
            }
        }
    }
)
async def evaluate_candidate(request: CandidateEvaluateRequest):
    """
    Evaluates a candidate's English accent from a provided video URL, returning the accent classification,
    confidence score, and an optional summary. Handles errors for non-English speakers, invalid input,
    video conversion, audio extraction, and internal failures with appropriate HTTP responses.

    Parameters:
        request (CandidateEvaluateRequest): Request body containing the video URL.

    Returns:
        CandidateEvaluateResponse: Accent classification, confidence score, and summary if successful.

    Raises:
        HTTPException: For non-English speakers, invalid input, video conversion errors,
        audio extraction/transcription/summarization/classification failures, and internal errors.
    """
    try:
        url = request.video_url

        # Validate the video url
        if url is None:
            raise ValueError("Video URL is required.")

        # Start the classification task
        score, accent, summary = await candidate_evaluator_service.evaluate(
            video_url=request.video_url
        )
        return CandidateEvaluateResponse(
            classification=accent,
            confidence=score,
            summary=summary
        )
    except CandidateLanguageException as e:
        "This exception can be ignored due to a non-english speaker detected."
        detected_language = e.detected_language
        probability = e.probability
        logging.info(
            f'The candidate appears to be a {detected_language} speaker with probability {probability}.'
        )
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail={
                "detected_language": detected_language,
                "probability": probability,
                "message": "Non-English speaker detected."
            }
        )
    except ValueError as e:
        error_message = str(e)
        logging.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_message
        )
    except VideoConversionException as e:
        error_message = str(e)
        logging.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    except (
            AudioExtractionException, AudioTranscribeException,
            TranscriptionSummarizationException, EnglishAccentClassificationException
    ) as e:
        error_message = str(e)
        logging.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_message
        )
    except Exception as e:
        error_message = str(e)
        logging.error(error_message)
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred. Please try again later."
        )
