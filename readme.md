# Candidate English Accent Evaluator

A FastAPI service for evaluating spoken language, including accent identification and language processing, built with FastAPI and leveraging state-of-the-art speech and language models.

## Features

- **Accent Identification**: Uses a pre-trained ECAPA model for accent detection.
- **Speech & Language Processing**: Integrates with openai-whisper, fasttext, and langdetect for transcription and language detection.
- **API Service**: Exposes endpoints via FastAPI for easy integration.
- **Media Handling**: Supports audio extraction and processing from various sources, including **YouTube** and **Public .mp4 links**.

## Supported English Accents

```markdown
african
australia
bermuda
canada
england
hongkong
indian
ireland
malaysia
newzealand
philippines
scotland
singapore
southatlandtic
us
wales
```


## Requirements

- Python 3.11+
- See `requirements.txt` for all dependencies.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/spoken-language-evaluator.git
   cd spoken-language-evaluator
   ```

2. **Create and activate a virtual environment:**

   ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
   
### Note:

For GPU users, run the following commands soon after running the **requirements.txt**.
   ```bash
   pip uninstall torch torchvision torchaudio -y
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```

### Usage
- **Running the API Server**
    ```bash
    uvicorn main:app --reload
    ```

The API will be available at http://localhost:8000.

### Example API Endpoints
- **GET /health**: Application health checking.
- **POST** /transcribe: Submit an audio file for transcription.
Refer to the API documentation (Swagger /docs) for detailed endpoint usage.

### Model Files
- Pre-trained models are expected in the model_cache/ directory.
- The accent identification model and its configuration are referenced in .env and model_cache/accent-id-commonaccent_ecapa/hyperparams.yaml.

### Development
- Code style: Follow PEP8.
- Contributions are welcome! Please open issues or pull requests as needed.

Note: For best performance, ensure your system has access to a GPU when running speech models.