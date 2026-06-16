import json
import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pathlib import Path

from app.api.deps import get_current_user
from app.core.rate_limit import RATE_LIMITS, limiter
from app.models.user import User
from app.schemas.animation import AnimationResult, AnimationTimeline
from app.services.animation_service import render_animation_pipeline

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/animations", tags=["animations"])

ANIMATION_OUTPUT_DIR = Path("data/animations")


@router.post("/render")
@limiter.limit(RATE_LIMITS["api_write"])
async def render_animation(
    request: Request,
    body: AnimationTimeline,
    current_user: User = Depends(get_current_user),
):
    animation_id = uuid4()
    output_dir = ANIMATION_OUTPUT_DIR / str(animation_id)

    logger.info(
        "Animation render requested: id=%s title=%r user=%s",
        animation_id, body.title, current_user.id,
    )

    try:
        result = await render_animation_pipeline(body, output_dir)
    except Exception as e:
        logger.error("Animation rendering failed: id=%s error=%s", animation_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Animation rendering failed: {e}",
        )

    metadata_path = output_dir / "result.json"
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(
            {"id": str(animation_id), "result": result.model_dump(mode="json")},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    logger.info(
        "Animation render completed: id=%s status=%s",
        animation_id, result.status,
    )

    return {"id": animation_id, "result": result}


@router.get("/{animation_id}")
@limiter.limit(RATE_LIMITS["api_read"])
async def get_animation(
    request: Request,
    animation_id: UUID,
    current_user: User = Depends(get_current_user),
):
    metadata_path = ANIMATION_OUTPUT_DIR / str(animation_id) / "result.json"
    if not metadata_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Animation not found",
        )

    data = json.loads(metadata_path.read_text(encoding="utf-8"))
    result = AnimationResult(**data["result"])
    return {"id": animation_id, "result": result}
