import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..rag.graph import content_text, graph

router = APIRouter(prefix="/chat", tags=["chat"])


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    lang: str = "en"


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("")
async def chat(body: ChatRequest):
    state = {"messages": [m.model_dump() for m in body.messages], "lang": body.lang}

    async def stream():
        sources: list[dict] = []
        try:
            async for ev in graph.astream_events(state, version="v2"):
                kind = ev["event"]
                if kind == "on_chat_model_stream" and "final_answer" in (ev.get("tags") or []):
                    token = content_text(getattr(ev["data"].get("chunk"), "content", ""))
                    if token:
                        yield _sse("token", {"t": token})
                elif kind == "on_chain_end" and ev.get("name") == "retrieve":
                    out = ev["data"].get("output")
                    if isinstance(out, dict) and out.get("sources"):
                        sources = out["sources"]
        except Exception as exc:  # noqa: BLE001
            yield _sse("error", {"message": str(exc)})
        yield _sse("sources", {"sources": sources})
        yield _sse("done", {})

    return StreamingResponse(stream(), media_type="text/event-stream")
