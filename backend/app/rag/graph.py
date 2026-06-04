from functools import lru_cache
from typing import TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph

from ..config import get_settings
from .retrieve import retrieve


@lru_cache
def get_llm() -> ChatGoogleGenerativeAI:
    """Lazily built so the app boots even if GOOGLE_API_KEY isn't set yet."""
    s = get_settings()
    return ChatGoogleGenerativeAI(
        model=s.gemini_chat_model,
        google_api_key=s.google_api_key,
        temperature=0.2,
    )

SYSTEM = """You are the assistant on Tsai Cheng-Hung's (蔡承紘) personal website.

Rules:
- Answer ONLY using the provided context about Tsai, his projects, and his blog.
- Reply in {lang_name}.
- When relevant, cite sources as Markdown links using the EXACT URLs from the context
  (e.g. [the project](/projects/some-slug)). Never invent URLs or facts.
- If the context doesn't cover the question, say you're not sure and point to the homepage (/).
  Politely decline questions unrelated to Tsai, his work, or this site.
- Be concise, warm, and helpful.

Context:
{context}"""


def content_text(content) -> str:
    """Gemini chunks may be a str or a list of parts; flatten to text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out = []
        for part in content:
            if isinstance(part, str):
                out.append(part)
            elif isinstance(part, dict):
                out.append(part.get("text", ""))
        return "".join(out)
    return ""


CONDENSE = (
    "Rewrite the user's latest message into a single standalone search query in the SAME "
    "language as that message, resolving any pronouns or references using the conversation. "
    "Output ONLY the query text — no quotes, no preamble."
)


class ChatState(TypedDict, total=False):
    messages: list[dict]  # [{role: 'user'|'assistant', content: str}]
    lang: str
    query: str
    context: str
    sources: list[dict]
    answer: str


async def condense_node(state: ChatState) -> dict:
    """Turn a follow-up (with pronouns) into a standalone query for retrieval.
    First turn (no history) is used as-is to save a call."""
    messages = state.get("messages", [])
    last = messages[-1]["content"] if messages else ""
    if len(messages) <= 1:
        return {"query": last}

    lc = [SystemMessage(content=CONDENSE)]
    for m in messages[:-1]:
        lc.append(HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"]))
    lc.append(HumanMessage(content=last))
    try:
        resp = await get_llm().ainvoke(lc, {"tags": ["condense"]})
        q = content_text(resp.content).strip().strip('"').strip()
        return {"query": q or last}
    except Exception:  # noqa: BLE001
        return {"query": last}


async def retrieve_node(state: ChatState) -> dict:
    query = state.get("query") or ""
    if not query:
        msgs = state.get("messages", [])
        query = msgs[-1]["content"] if msgs else ""
    context, sources, _ = await retrieve(query, state.get("lang", "en"))
    return {"context": context, "sources": sources}


async def generate_node(state: ChatState) -> dict:
    lang = state.get("lang", "en")
    lang_name = "Traditional Chinese (繁體中文)" if lang == "zh" else "English"
    system = SYSTEM.format(lang_name=lang_name, context=state.get("context", ""))

    messages = state.get("messages", [])
    lc_messages = [SystemMessage(content=system)]
    for m in messages[:-1]:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        else:
            lc_messages.append(AIMessage(content=m["content"]))
    if messages:
        lc_messages.append(HumanMessage(content=messages[-1]["content"]))

    parts: list[str] = []
    async for chunk in get_llm().astream(lc_messages, {"tags": ["final_answer"]}):
        parts.append(content_text(chunk.content))
    return {"answer": "".join(parts)}


def build_graph():
    g = StateGraph(ChatState)
    g.add_node("condense", condense_node)
    g.add_node("retrieve", retrieve_node)
    g.add_node("generate", generate_node)
    g.add_edge(START, "condense")
    g.add_edge("condense", "retrieve")
    g.add_edge("retrieve", "generate")
    g.add_edge("generate", END)
    return g.compile()


graph = build_graph()
