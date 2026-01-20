from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.models.schemas import TransformRequest, TransformResponse, ErrorResponse
from app.services.llm_service import LLMService, get_llm_service
from app.services.transformer import TransformerService

router = APIRouter(prefix="/api/v1", tags=["transform"])


@router.post(
    "/transform",
    response_model=TransformResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def transform_report(
    request: TransformRequest,
    llm_service: LLMService = Depends(get_llm_service),
) -> TransformResponse:
    """Transform an IC research report into LinkedIn, Newsletter, and WhatsApp formats."""
    try:
        transformer = TransformerService(llm_service)
        result = await transformer.transform(request.report_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transform/stream")
async def transform_report_stream(
    request: TransformRequest,
    llm_service: LLMService = Depends(get_llm_service),
):
    """Stream the transformation of an IC research report with typewriter effect."""
    transformer = TransformerService(llm_service)

    return StreamingResponse(
        transformer.transform_stream(
            request.report_text,
            request.tone,
            request.variant.value if request.variant else "A"
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
