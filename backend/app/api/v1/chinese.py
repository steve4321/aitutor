from datetime import datetime, timezone
from uuid import NAMESPACE_DNS, UUID, uuid5

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_current_user
from app.core.rate_limit import RATE_LIMITS, limiter
from app.models.user import User
from app.schemas.chinese import (
    CompositionTaskResponse,
    PoetryListResponse,
    PoetryResponse,
)

router = APIRouter(prefix="/chinese", tags=["chinese"])

_BASE_TIME = datetime(2024, 9, 1, tzinfo=timezone.utc)


def _stable_seed_id(domain: str, index: int) -> UUID:
    return uuid5(NAMESPACE_DNS, f"{domain}-{index}")


_COMPOSITION_TASKS: list[CompositionTaskResponse] = [
    CompositionTaskResponse(
        id=_stable_seed_id("chinese-composition", 1),
        title="我最喜欢的一本书",
        writing_type="narrative",
        prompt=(
            "请以《我最喜欢的一本书》为题写一篇记叙文。"
            "介绍你最喜欢的一本书，说明喜欢的理由，"
            "可以谈谈书中的故事情节、人物形象或让你感动的地方。"
            "注意条理清晰，语句通顺，表达自己的真实感受。"
        ),
        min_chars=300,
        max_chars=600,
        created_at=_BASE_TIME,
    ),
    CompositionTaskResponse(
        id=_stable_seed_id("chinese-composition", 2),
        title="一件难忘的事",
        writing_type="narrative",
        prompt=(
            "请以《一件难忘的事》为题写一篇记叙文。"
            "回忆你生活中印象最深的一件事，按事情发展的顺序写清楚起因、经过和结果。"
            "注意把最难忘的部分写具体，加入自己的心理活动和感受。"
        ),
        min_chars=300,
        max_chars=600,
        created_at=_BASE_TIME,
    ),
    CompositionTaskResponse(
        id=_stable_seed_id("chinese-composition", 3),
        title="美丽的秋天",
        writing_type="descriptive",
        prompt=(
            "请以《美丽的秋天》为题写一篇描写文。"
            "仔细观察秋天的景色，从颜色、声音、气味等方面描写秋天的特点。"
            "运用比喻、拟人等修辞手法，让文章更生动形象。"
        ),
        min_chars=300,
        max_chars=600,
        created_at=_BASE_TIME,
    ),
    CompositionTaskResponse(
        id=_stable_seed_id("chinese-composition", 4),
        title="我的校园",
        writing_type="descriptive",
        prompt=(
            "请以《我的校园》为题写一篇描写文。"
            "按照一定的方位顺序（如从外到内、从远到近）介绍你的校园。"
            "描写校园里的建筑物、花草树木和同学们活动的场景，展现校园的美丽和活力。"
        ),
        min_chars=300,
        max_chars=600,
        created_at=_BASE_TIME,
    ),
    CompositionTaskResponse(
        id=_stable_seed_id("chinese-composition", 5),
        title="如果我有一双翅膀",
        writing_type="imaginative",
        prompt=(
            "请以《如果我有一双翅膀》为题写一篇想象作文。"
            "展开丰富的想象，假如你有一双翅膀，你会飞到哪里？看到什么？做什么？"
            "大胆想象，合理构思，让故事既有趣又有意义。"
        ),
        min_chars=300,
        max_chars=600,
        created_at=_BASE_TIME,
    ),
    CompositionTaskResponse(
        id=_stable_seed_id("chinese-composition", 6),
        title="二十年后的我",
        writing_type="imaginative",
        prompt=(
            "请以《二十年后的我》为题写一篇想象作文。"
            "想象二十年后的你会是什么样子？从事什么工作？过着怎样的生活？"
            "结合自己的理想和愿望，合理想象，表达对未来的憧憬。"
        ),
        min_chars=300,
        max_chars=600,
        created_at=_BASE_TIME,
    ),
    CompositionTaskResponse(
        id=_stable_seed_id("chinese-composition", 7),
        title="给老师的一封信",
        writing_type="practical",
        prompt=(
            "请以《给老师的一封信》为题写一封应用文（书信）。"
            "注意书信的正确格式（称呼、问候语、正文、祝语、署名、日期）。"
            "向老师表达感谢之情，可以回忆一件与老师之间难忘的事，语言真诚得体。"
        ),
        min_chars=300,
        max_chars=600,
        created_at=_BASE_TIME,
    ),
    CompositionTaskResponse(
        id=_stable_seed_id("chinese-composition", 8),
        title="观察日记——种豆芽",
        writing_type="practical",
        prompt=(
            "请以《观察日记——种豆芽》为题写一篇应用文（观察日记）。"
            "记录你种豆芽的过程，包括泡豆子、每天的变化和最终的结果。"
            "按日期记录，注意观察细致，描写准确，格式正确。"
        ),
        min_chars=300,
        max_chars=600,
        created_at=_BASE_TIME,
    ),
]


_POEMS: list[PoetryResponse] = [
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 1),
        title="春晓",
        poet="孟浩然",
        dynasty="唐",
        theme="seasonal",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 2),
        title="绝句",
        poet="杜甫",
        dynasty="唐",
        theme="seasonal",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 3),
        title="江雪",
        poet="柳宗元",
        dynasty="唐",
        theme="seasonal",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 4),
        title="小池",
        poet="杨万里",
        dynasty="宋",
        theme="seasonal",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 5),
        title="登鹳雀楼",
        poet="王之涣",
        dynasty="唐",
        theme="landscape",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 6),
        title="望庐山瀑布",
        poet="李白",
        dynasty="唐",
        theme="landscape",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 7),
        title="鹿柴",
        poet="王维",
        dynasty="唐",
        theme="landscape",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 8),
        title="望天门山",
        poet="李白",
        dynasty="唐",
        theme="landscape",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 9),
        title="饮湖上初晴后雨",
        poet="苏轼",
        dynasty="宋",
        theme="landscape",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 10),
        title="静夜思",
        poet="李白",
        dynasty="唐",
        theme="emotions",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 11),
        title="游子吟",
        poet="孟郊",
        dynasty="唐",
        theme="emotions",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 12),
        title="赋得古原草送别",
        poet="白居易",
        dynasty="唐",
        theme="emotions",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 13),
        title="示儿",
        poet="陆游",
        dynasty="宋",
        theme="emotions",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 14),
        title="题西林壁",
        poet="苏轼",
        dynasty="宋",
        theme="masters",
        created_at=_BASE_TIME,
    ),
    PoetryResponse(
        id=_stable_seed_id("chinese-poetry", 15),
        title="咏鹅",
        poet="骆宾王",
        dynasty="唐",
        theme="masters",
        created_at=_BASE_TIME,
    ),
]


@router.get("/composition/tasks", response_model=list[CompositionTaskResponse])
@limiter.limit(RATE_LIMITS["api_read"])
async def list_composition_tasks(
    request: Request,
    current_user: User = Depends(get_current_user),
    limit: int = 50,
):
    return _COMPOSITION_TASKS[:limit]


@router.get("/poetry", response_model=PoetryListResponse)
@limiter.limit(RATE_LIMITS["api_read"])
async def list_poems(
    request: Request,
    current_user: User = Depends(get_current_user),
    limit: int = 100,
):
    items = _POEMS[:limit]
    return PoetryListResponse(items=items, total=len(items))
