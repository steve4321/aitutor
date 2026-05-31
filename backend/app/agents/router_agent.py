"""Router node: classifies user intent and routes to appropriate agent."""
import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

ROUTER_SYSTEM_PROMPT = """You are an intent classifier for an AI tutoring system.
Classify the user's message into exactly ONE intent and target agent.

Possible intents:
- "learn": Student wants to learn a concept, start a lesson, or continue course mode
- "practice": Student wants to solve problems, get hints, or is working on a problem
- "assess": Student is submitting an answer for evaluation
- "ask": Student is asking a general question about a topic
- "manage": Student wants to see progress, get recommendations, or change settings

Possible target agents:
- "tutor": For teaching, conversation, Socratic dialogue, concept explanation
- "assessor": For scoring, evaluating answers, error diagnosis
- "curriculum": For scheduling, recommendations, progress tracking

Possible subjects:
- "amc_math": Math competition topics
- "ket_english": KET English exam topics
- "chn_composition": Chinese composition/writing
- "chn_poetry": Classical Chinese poetry

Possible session modes:
- "course": Systematic lesson learning
- "practice": Problem-solving practice
- "review": Spaced repetition review
- "diagnostic": Assessment/diagnostic test

Respond with ONLY a JSON object:
{"intent": "...", "target_agent": "...", "subject": "...", "session_mode": "..."}"""

INTENT_RULES = {
    "assess": ["提交", "submit", "答案", "answer is", "我写完了", "done writing"],
    "practice": ["提示", "hint", "不会", "stuck", "help", "下一题", "next problem", "再来一道"],
    "learn": ["学", "learn", "课程", "lesson", "教我", "teach me", "讲解", "explain"],
    "manage": ["进度", "progress", "推荐", "recommend", "复习", "review", "设置"],
}


def _rule_based_classify(message: str, request_type: str) -> dict:
    """Fallback classifier when LLM is unavailable."""
    if request_type == "attempt":
        return {
            "intent": "assess",
            "target_agent": "assessor",
            "subject": "amc_math",
            "session_mode": "practice",
        }

    msg_lower = message.lower()
    for intent, keywords in INTENT_RULES.items():
        if any(kw in msg_lower for kw in keywords):
            target = "assessor" if intent == "assess" else "tutor"
            if intent == "manage":
                target = "curriculum"
            return {
                "intent": intent,
                "target_agent": target,
                "subject": "amc_math",
                "session_mode": "practice",
            }

    return {
        "intent": "ask",
        "target_agent": "tutor",
        "subject": "amc_math",
        "session_mode": "practice",
    }


async def router_node(state: AgentState) -> dict:
    """Classify intent and route to appropriate agent."""

    if state.get("request_type") == "attempt":
        return {
            "intent": "assess",
            "target_agent": "assessor",
            "subject": (state.get("problem_data") or {}).get("subject", "amc_math"),
            "session_mode": "practice",
        }

    if state.get("request_type") == "session_init":
        return {
            "intent": "manage",
            "target_agent": "curriculum",
            "subject": "amc_math",
            "session_mode": "practice",
        }

    user_message = state.get("user_message", "")
    request_type = state.get("request_type", "chat")

    llm = get_llm("fast")
    if llm is not None:
        try:
            messages = [
                SystemMessage(content=ROUTER_SYSTEM_PROMPT),
                HumanMessage(content=user_message),
            ]
            response = await llm.ainvoke(messages)
            result = json.loads(response.content)
            return {
                "intent": result.get("intent", "ask"),
                "target_agent": result.get("target_agent", "tutor"),
                "subject": result.get("subject", "amc_math"),
                "session_mode": result.get("session_mode", "practice"),
            }
        except Exception:
            logger.warning("LLM router failed, falling back to rules")

    return _rule_based_classify(user_message, request_type)
