"""
API endpoints for text ingestion.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.source import SourceTextRequest, SourceTextResponse
from app.services.ingest_service import get_ingest_service
from app.services.extract_service import get_extract_service, ExtractionError
from app.services.verification_service import VerificationService
from app.services.graph_store import get_graph_store
from app.utils.ollama_client import get_ollama_client, OllamaConnectionError, OllamaTimeoutError

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("", response_model=SourceTextResponse)
async def ingest_text(
    request: SourceTextRequest,
    db: Session = Depends(get_db)
):
    """
    Ingest German text and extract learnable items.

    This endpoint:
    1. Extracts items and relationships using LLM
    2. Verifies items appear in source text (hallucination prevention)
    3. Computes canonical forms and deduplicates
    4. Stores verified items in database
    5. Creates initial encounter records
    """
    try:
        # Get dependencies
        ollama_client = get_ollama_client()
        extract_service = get_extract_service(ollama_client)
        verification_service = VerificationService(db, ollama_client)  # NEW
        graph_store = get_graph_store(db)
        ingest_service = get_ingest_service(
            db,
            extract_service,
            verification_service,  # NEW
            graph_store
        )

        # Process text
        result = await ingest_service.process_text(request.text)

        return SourceTextResponse(**result)

    except OllamaConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Ollama: {str(e)}"
        )
    except OllamaTimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail=f"Ollama request timed out: {str(e)}"
        )
    except ExtractionError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
